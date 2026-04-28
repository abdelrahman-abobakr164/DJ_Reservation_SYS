from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .tasks import send_email_to_users
from django.utils.text import slugify
from django.core.cache import cache
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone
from django.http import QueryDict
from django.db import transaction
from datetime import date
from core.models import *
from core.forms import *


User = get_user_model()


def agents(request):
    users = User.objects.prefetch_related("specialties")
    return render(request, "core/agents.html", {"users": users})


@require_http_methods(["GET", "POST"])
def agent_detail(request, username):
    cache_key = f"agent_detail_{slugify(username)}"
    agent = cache.get(cache_key)
    if not agent:
        agent = get_object_or_404(
            User.objects.prefetch_related(
                "working_hours",
                "graduation",
                "certifications",
                "specialties",
                "recent_achievements",
            ),
            username=username,
        )
        cache.set(cache_key, agent, timeout=60 * 15)

    if request.method == "POST":
        form = ReservationForm(request.POST, agent=agent)
        if not form.is_valid():
            messages.error(request, "Please Correct the errors in this form")
            return redirect("agent_detail", username=agent.username)

        return _handle_reservation(request, form, agent)

    form = ReservationForm(agent=agent)
    return render(request, "core/agent_detail.html", {"agent": agent, "form": form})


def _handle_reservation(request, form, agent):
    today = timezone.now().date()

    time = form.cleaned_data["time"]
    date = form.cleaned_data["date"]
    email = form.cleaned_data["email"]
    subject = form.cleaned_data["subject"]
    full_name = form.cleaned_data["full_name"]

    day_of_week = date.weekday()

    if agent.number_of_reservations == agent.appointments and date == today:
        messages.warning(request, "Applications are Closed for Today.")
        return redirect("agent_detail", username=agent.username)

    subForm = form.save(commit=False)
    subForm.agent = agent

    if not subForm.is_available():
        messages.warning(request, "This Time Is Already Booked")

    try:
        with transaction.atomic():
            agent_working_day = ELDay.objects.get(agent=agent, day_of_week=day_of_week)

            if time < agent_working_day.start_time:
                messages.warning(request, "it's too earlier.")
            if time >= agent_working_day.end_time:
                messages.warning(request, "it's too Late.")

            subForm.save()

            transaction.on_commit(
                lambda: send_email_to_users.delay(
                    f"Thank You for Your Reservation {full_name}",
                    f"Your {subject} Was Sent To {agent.username} and I Will Answer Send You an Email You Very Soon if there a place For You",
                    agent.email,
                    email,
                )
            )

            messages.success(
                request, f"Your Reservation Has Been Submitted successfully."
            )

    except ELDay.DoesNotExist:
        messages.warning(request, f"{agent.username} Not Available at This Time")

    return redirect("agent_detail", username=agent.username)


@login_required
def reservations_list(request, username):
    agent = get_object_or_404(User, username=username)

    if request.user.username != agent.username:
        raise PermissionDenied

    today = date.today()

    reservations = (
        Reservation.objects.filter(agent=agent, status="Confirmed", date=today)
        .select_related("agent")
        .order_by("date")
    )
    sort_by_dates = (
        Reservation.objects.filter(agent=agent, status="Confirmed", date__gt=today)
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

    sort_by = clean_params.get("sort_by")
    calendar = clean_params.get("calendar")

    if sort_by == "all":
        reservations = Reservation.objects.filter(
            agent=agent, status="Confirmed", date__gte=today
        ).select_related("agent")
    elif sort_by and sort_by != "today":
        reservations = Reservation.objects.filter(
            agent=agent, status="Confirmed", date=sort_by
        ).select_related("agent")

    if calendar:
        reservations = Reservation.objects.filter(
            agent=agent, status="Confirmed", date=calendar
        ).select_related("agent")

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


@require_http_methods(["GET", "POST"])
@login_required
def scheduled_reservations(request, username):
    agent = get_object_or_404(User, username=username)
    today = timezone.now().date()

    if request.user.username != agent.username:
        raise PermissionDenied

    reservations = Reservation.objects.filter(
        agent=agent, status="Pending", date__gte=today
    )

    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        action = request.POST.get("action")
        return _handle_scheduled_reservation(request, agent, action, reservation_id)

    return render(
        request, "core/scheduled_reservations.html", {"reservations": reservations}
    )


def _handle_scheduled_reservation(request, agent, action, reservation_id):
    today = timezone.now().date()
    try:
        with transaction.atomic():
            reservation = get_object_or_404(Reservation, id=reservation_id)
            scheduled_dates = Reservation.objects.filter(
                date=reservation.date, status="Confirmed"
            )
            if action == "Accept":
                if reservation.date == today:
                    if agent.appointments < agent.number_of_reservations:
                        reservation.status = "Confirmed"
                        agent.appointments += 1
                        transaction.on_commit(
                            lambda: send_email_to_users.delay(
                                f"Your {reservation.subject} To {agent.username}",
                                f"Your {reservation.subject}  To {agent.username} Has Been Confirmed You Can Do {reservation.subject} on {reservation.date} At {reservation.time}",
                                agent.email,
                                reservation.email,
                            )
                        )
                        messages.success(
                            request, "the appointment has been submitted successfully!"
                        )
                        return redirect(
                            "scheduled_reservations", username=agent.username
                        )
                    else:
                        messages.warning(
                            request,
                            "You've reached Your Number Of Rerservations Today, If You Want More You Can Increase Your Number Of Rerservations in Account",
                        )
                        return redirect(
                            "scheduled_reservations", username=agent.username
                        )

                elif (
                    reservation.date > today
                    and scheduled_dates.count() == agent.number_of_reservations
                ):
                    messages.warning(
                        request,
                        f"You've reached Your Number Of Rerservations on {reservation.date}, If You Want More You Can Increase Your Number Of Rerservations in Account",
                    )
                    return redirect("scheduled_reservations", username=agent.username)

                elif reservation.date < today:
                    messages.warning(request, "The Date is passed")
                    return redirect("scheduled_reservations", username=agent.username)
                else:
                    reservation.status = "Confirmed"
                    transaction.on_commit(
                        lambda: send_email_to_users.delay(
                            f"Your {reservation.subject} To {agent.username}",
                            f"Your {reservation.subject}  To {agent.username} Has Been Confirmed You Can Do {reservation.subject} on {reservation.date} At {reservation.time}",
                            agent.email,
                            reservation.email,
                        )
                    )
                    messages.success(
                        request, "the appointment has been submitted successfully!"
                    )
                    return redirect("scheduled_reservations", username=agent.username)
            elif action == "Cancel":
                reservation.status = "Cancelled"
                transaction.on_commit(
                    lambda: send_email_to_users.delay(
                        f"Your {reservation.subject} To {agent.username}",
                        f"Your {reservation.subject}  To {agent.username} Has Been Cancelled You Can Try Again",
                        agent.email,
                        reservation.email,
                    )
                )
            else:
                messages.error(request, "Wrong Action. Please try again")
                return redirect("scheduled_reservations", username=agent.username)

            agent.save()
            reservation.save()
            return redirect("scheduled_reservations", username=agent.username)

    except Reservation.DoesNotExist:
        messages.error(request, "Wrong Reservation")

    return redirect("scheduled_reservations", username=agent.username)
