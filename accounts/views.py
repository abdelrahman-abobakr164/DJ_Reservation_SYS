from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction

from .decorators import authenticated_and_owner
from accounts.forms import *


User = get_user_model()


@login_required
@authenticated_and_owner(User)
def edit(request, username):
    agent = get_object_or_404(User, username=username)
    form = UserForm(instance=agent)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=agent)
        if form.is_valid():
            form.save()
            return redirect("account", username=agent.username)
        else:
            messages.error(request, f"Please correct the errors in the form.")
    return render(request, "accounts/account.html", {"form": form, "agent": agent})


@login_required
@authenticated_and_owner(User)
def working_times(request, username):
    agent = get_object_or_404(
        User.objects.prefetch_related("working_hours"), username=username
    )
    form = WorkingTimesForm()

    if request.method == "POST":
        action = request.POST.get("action")
        elday_id = request.POST.get("working_time_id")

        if action == "Remove":
            work_time_id = get_object_or_404(ELDay, id=elday_id, agent=agent)
            work_time_id.delete()
            messages.success(request, "Working Time Removed.")
            return redirect("working-times", username=agent.username)
        else:
            form = WorkingTimesForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        subForm = form.save(commit=False)
                        subForm.agent = agent
                        subForm.save()
                        agent.working_hours.add(subForm)
                        messages.success(request, "Working Time Added.")
                        return redirect("working-times", username=agent.username)
                except:
                    messages.error(request, "Somthing went wrong. please try again")
            else:
                messages.error(request, "Please correct the errors in the form")

    context = {"agent": agent, "form": form}
    return render(request, "accounts/working_times.html", context)


@login_required
@authenticated_and_owner(User)
def graduations(request, username):
    agent = get_object_or_404(
        User.objects.prefetch_related("graduation"), username=username
    )
    form = GraduationForm()
    if request.method == "POST":
        action = request.POST.get("action")
        graduation_id = request.POST.get("graduation_id")

        if action == "Remove":
            grad_id = get_object_or_404(Graduation, id=graduation_id)
            grad_id.delete()
            messages.success(request, "Graduation record removed")
            return redirect("graduations", username=agent.username)
        else:
            form = GraduationForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        savingForm = form.save()
                        agent.graduation.add(savingForm)
                    messages.success(request, " Graduation Record Added.")
                    return redirect("graduations", username=agent.username)
                except Exception:
                    messages.error(request, "something went wrong. please try again")
            else:
                messages.error(request, "Please correct the errors in the form.")
                return redirect("graduations", username=agent.username)

    context = {"agent": agent, "Graduationform": form}
    return render(request, "accounts/graduations.html", context)


@login_required
@authenticated_and_owner(User)
def certifications(request, username):
    agent = get_object_or_404(
        User.objects.prefetch_related("certifications"), username=username
    )
    form = CertificationsForm()

    if request.method == "POST":
        action = request.POST.get("action")
        certifications_id = request.POST.get("certifications_id")

        if action == "Remove":
            cert_id = get_object_or_404(Certification, id=certifications_id)
            cert_id.delete()
            return redirect("certifications", username=agent.username)
        else:
            form = CertificationsForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        savingForm = form.save()
                        agent.certifications.add(savingForm)
                    messages.success(request, "Certification Added Successfully!")
                    return redirect("certifications", username=agent.username)

                except Exception:
                    messages.error(request, "Something Went wrong. please try again")
            else:
                messages.error(request, "Please correct the errors in the form.")
                return redirect("certifications", username=agent.username)

    context = {"agent": agent, "Certificationsform": form}
    return render(request, "accounts/certifications.html", context)


@login_required
@authenticated_and_owner(User)
def recent_achievements(request, username):
    agent = get_object_or_404(
        User.objects.prefetch_related("recent_achievements"), username=username
    )
    form = RecentAchievementsForm()
    if request.method == "POST":
        action = request.POST.get("action")
        recent_achievements_id = request.POST.get("recent_achievements_id")

        if action == "Remove":
            recent_id = get_object_or_404(RecentAchievement, id=recent_achievements_id)
            recent_id.delete()
            messages.success(request, "achievement Removed Successfully!")
            return redirect("recent_achievements", username=agent.username)
        else:
            form = RecentAchievementsForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        savingForm = form.save()
                        agent.recent_achievements.add(savingForm)
                    messages.success(request, "recent_achievements Added Successfully!")
                    return redirect("recent_achievements", username=agent.username)
                except Exception:
                    messages.error(request, "Something Went Wrong. Please try Again")
            else:
                messages.error(request, "please correct the errors in the form")

    context = {"agent": agent, "RecentAchievementsform": form}
    return render(request, "accounts/recent_achievements.html", context)


@login_required
@authenticated_and_owner(User)
def specialties(request, username):
    agent = get_object_or_404(
        User.objects.prefetch_related("specialties"), username=username
    )
    form = SpecialtiesForm()
    if request.method == "POST":
        action = request.POST.get("action")
        specialties_id = request.POST.gt("specialties_id")

        if action == "Remove":
            specialtie_id = get_object_or_404(Specialtie, id=specialties_id)
            specialtie_id.delete()
            messages.success(request, "specialty Removed Successfully!")
            return redirect("specialties", username=agent.username)
        else:
            form = SpecialtiesForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        savingForm = form.save()
                        agent.specialties.add(savingForm)
                    messages.success(request, "specialties Added Successfully!")
                    return redirect("specialties", username=agent.username)
                except Exception:
                    messages.error(request, "Something Went Wrong. Please try Again")
            else:
                messages.error(request, "please correct the errors in the form")

    context = {"agent": agent, "Specialtiesform": form}
    return render(request, "accounts/specialties.html", context)
