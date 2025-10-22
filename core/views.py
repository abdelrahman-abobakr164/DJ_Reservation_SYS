from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .tasks import send_email_to_users
from django.utils.text import slugify
from django.core.cache import cache
from django.contrib import messages
from collections import defaultdict
from django.http import QueryDict
from datetime import datetime
from datetime import date
from core.models import *
from core.forms import *


User = get_user_model()


def agents(request):
    users = cache.get("all_agents")
    if not users:
        users = list(User.objects.all())
        cache.set("all_agents", users, timeout=60 * 15)
    return render(request, "core/agents.html", {"users": users})


def agent_detail(request, username):
    cache_key = f"agent_detail_{slugify(username)}"
    agent = cache.get(cache_key)
    if not agent:
        agent = get_object_or_404(User, username=username)
        cache.set(cache_key, agent, timeout=60 * 15)

    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        form = ReservationForm(request.POST, agent=agent)
        if form.is_valid():
            subForm = form.save(commit=False)
            subForm.agent = agent
            time = form.cleaned_data.get("time")
            date = form.cleaned_data.get("date")
            email_form = form.cleaned_data.get("email")
            subject_form = form.cleaned_data.get("subject")

            day_of_week = date.weekday()
            if (
                agent.number_of_reservations == agent.appointments
                and date == datetime.now().date()
            ):
                messages.warning(request, "Applications are Now Closed For Today.")
            else:
                if subForm.is_available():
                    try:
                        agent_working_day = ELDay.objects.get(
                            agent=agent, day_of_week=day_of_week
                        )
                        if time < agent_working_day.start_time:
                            messages.warning(request, "it's too earlier.")
                        elif time >= agent_working_day.end_time:
                            messages.warning(request, "it's too Late.")
                        else:

                            send_email_to_users(
                                f"Thank You for Your Reservation {form.cleaned_data.get('full_name')}",
                                f"Your {subject_form} Was Sent To {agent.username} and I Will Answer Send You an Email You Very Soon if there a place For You",
                                agent.email,
                                email_form,
                            )
                            subForm.save()

                            messages.success(
                                request, f"Your Reservation Has Been Sented."
                            )
                            return redirect(url)

                    except ELDay.DoesNotExist:
                        messages.warning(
                            request,
                            f"The {agent.username} is Not Available at This Time",
                        )
                else:
                    messages.warning(request, "This Time Is Already Booked")
    else:
        form = ReservationForm(agent=agent)
    return render(request, "core/agent_detail.html", {"agent": agent, "form": form})


def reservations_list(request, username):
    agent = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user.username == agent.username:
        today = date.today()

        reservations = Reservation.objects.filter(
            agent=agent, status="Confirmed", date=today
        )
        sort_by_dates = (
            Reservation.objects.filter(agent=agent, status="Confirmed", date__gte=today)
            .values_list("date", flat=True)
            .distinct()
            .order_by("date")
        )

        params = request.GET.copy()
        clean_params = QueryDict(mutable=True)

        for key, value in params.items():
            if value and value.strip():
                clean_params[key] = value

        if len(params) != len(clean_params):
            if clean_params:
                return redirect(f"{request.path}?{clean_params.urlencode()}")
            else:
                return redirect(f"{request.path}")

        sort_by = request.GET.get("sort_by")
        calendar = request.GET.get("calendar")

        if clean_params.get("sort_by") == "all":
            reservations = Reservation.objects.filter(
                agent=agent, status="Confirmed", date__gte=today
            )
        elif clean_params.get("sort_by") and clean_params.get("sort_by") != "today":
            reservations = Reservation.objects.filter(
                agent=agent, status="Confirmed", date=sort_by
            )

        if clean_params.get("calendar"):
            reservations = Reservation.objects.filter(
                agent=agent, status="Confirmed", date=calendar
            )

        reservation_by_date = defaultdict(list)
        for i in reservations:
            reservation_by_date[i.date].append(i)

        context = {
            "sort_by_dates": sort_by_dates,
            "today": today,
            "agent": agent,
            "reservation_by_date": dict(reservation_by_date),
        }
        return render(request, "core/reservations.html", context)
    else:
        return redirect("agent_detail", username=username)


def scheduled_reservations(request, username):
    agent = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user.username == agent.username:
        url = request.META.get("HTTP_REFERER")
        reservations = Reservation.objects.filter(agent=agent, status="Pending")
        if request.method == "POST":
            try:
                reservation_id = request.POST.get("reservation_id")
                action = request.POST.get("action")
                reservation = get_object_or_404(Reservation, id=reservation_id)
                scheduled_dates = Reservation.objects.filter(
                    date=reservation.date, status="Confirmed"
                )
                if action:
                    if action == "Accept":
                        if reservation.date == date.today():
                            if agent.appointments < agent.number_of_reservations:
                                reservation.status = "Confirmed"
                                agent.appointments += 1
                                send_email_to_users(
                                    f"Your {reservation.subject} To {agent.username}",
                                    f"Your {reservation.subject}  To {agent.username} Has Been Confirmed You Can Do {reservation.subject} on {reservation.date} At {reservation.time}",
                                    agent.email,
                                    reservation.email,
                                )
                            else:
                                messages.warning(
                                    request,
                                    "You've reached Your Number Of Rerservations Today, If You Want More You Can Increase Your Number Of Rerservations in Account",
                                )
                                return redirect(url)

                        elif (
                            reservation.date > date.today()
                            and scheduled_dates.count() == agent.number_of_reservations
                        ):
                            messages.warning(
                                request,
                                f"You've reached Your Number Of Rerservations on {reservation.date}, If You Want More You Can Increase Your Number Of Rerservations in Account",
                            )
                            return redirect(url)
                        elif reservation.date < date.today():
                            messages.warning(request, "Don't Mess")
                            return redirect(url)
                        else:
                            reservation.status = "Confirmed"
                            send_email_to_users(
                                f"Your {reservation.subject} To {agent.username}",
                                f"Your {reservation.subject}  To {agent.username} Has Been Confirmed You Can Do {reservation.subject} on {reservation.date} At {reservation.time}",
                                agent.email,
                                reservation.email,
                            )
                    elif action == "Cancel":
                        reservation.status = "Cancelled"
                        send_email_to_users(
                            f"Your {reservation.subject} To {agent.username}",
                            f"Your {reservation.subject}  To {agent.username} Has Been Cancelled You Can Try Again",
                            agent.email,
                            reservation.email,
                        )
                    else:
                        messages.error(request, "Don't Mess")
                        return redirect(url)
                    agent.save()
                    reservation.save()
                    return redirect(url)
            except Reservation.DoesNotExist:
                return None
        return render(
            request, "core/scheduled_reservations.html", {"reservations": reservations}
        )
    else:
        return redirect("agent_detail", username=username)
