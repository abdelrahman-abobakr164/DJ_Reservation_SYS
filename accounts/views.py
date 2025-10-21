from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .decorators import authenticated_and_owner
from django.contrib import messages
from accounts.forms import *
from django.contrib.auth.decorators import login_required


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
            messages.error(request, f"Don't Mess, {form.errors.as_ul}")
    return render(request, "accounts/account.html", {"form": form, "agent": agent})


@login_required
@authenticated_and_owner(User)
def working_times(request, username):
    agent = get_object_or_404(User, username=username)
    form = WorkingTimesForm()
    url = request.META.get("HTTP_REFERER")
    WorkingTimes = ELDay.objects.filter(agent=agent)

    if request.method == "POST":
        action = request.POST.get("action")
        elday_id = request.POST.get("working_time_id")

        if action:
            if action == "Remove":
                work_time_id = get_object_or_404(ELDay, id=elday_id)
                work_time_id.delete()
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")
                return redirect(url)
        else:
            form = WorkingTimesForm(request.POST)
            if form.is_valid():
                subForm = form.save(commit=False)
                subForm.agent = agent
                subForm.save()
                agent.working_hours.add(subForm)
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")

    context = {"WorkingTimes": WorkingTimes, "form": form}
    return render(request, "accounts/working_times.html", context)


@login_required
@authenticated_and_owner(User)
def graduations(request, username):
    agent = get_object_or_404(User, username=username)
    form = GraduationForm()
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        action = request.POST.get("action")
        graduation_id = request.POST.get("graduation_id")

        if action:
            if action == "Remove":
                grad_id = get_object_or_404(Graduation, id=graduation_id)
                grad_id.delete()
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")
                return redirect(url)
        else:
            form = GraduationForm(request.POST, request.FILES)
            if form.is_valid():
                savingForm = form.save()
                agent.graduation.add(savingForm)
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")

    context = {"agent": agent, "Graduationform": form}
    return render(request, "accounts/graduations.html", context)


@login_required
@authenticated_and_owner(User)
def certifications(request, username):
    agent = get_object_or_404(User, username=username)
    form = CertificationsForm()
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        action = request.POST.get("action")
        certifications_id = request.POST.get("certifications_id")

        if action:
            if action == "Remove":
                cert_id = get_object_or_404(Certification, id=certifications_id)
                cert_id.delete()
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")
                return redirect(url)
        else:
            form = CertificationsForm(request.POST, request.FILES)
            if form.is_valid():
                savingForm = form.save()
                agent.certifications.add(savingForm)
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")

    context = {"agent": agent, "Certificationsform": form}
    return render(request, "accounts/certifications.html", context)


@login_required
@authenticated_and_owner(User)
def recent_achievements(request, username):
    agent = get_object_or_404(User, username=username)
    form = RecentAchievementsForm()
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        action = request.POST.get("action")
        recent_achievements_id = request.POST.get("recent_achievements_id")

        if action:
            if action == "Remove":
                recent_id = get_object_or_404(
                    RecentAchievement, id=recent_achievements_id
                )
                recent_id.delete()
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")
                return redirect(url)
        else:
            form = RecentAchievementsForm(request.POST)
            if form.is_valid():
                savingForm = form.save()
                agent.recent_achievements.add(savingForm)
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")

    context = {"agent": agent, "RecentAchievementsform": form}
    return render(request, "accounts/recent_achievements.html", context)


@login_required
@authenticated_and_owner(User)
def specialties(request, username):
    agent = get_object_or_404(User, username=username)
    url = request.META.get("HTTP_REFERER")
    form = SpecialtiesForm()
    if request.method == "POST":
        action = request.POST.get("action")

        if action:
            if action == "Remove":
                specialties_id = request.POST.get("specialties_id")
                specialtie_id = get_object_or_404(Specialtie, id=specialties_id)
                specialtie_id.delete()
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")
                return redirect(url)
        else:
            form = SpecialtiesForm(request.POST)
            if form.is_valid():
                savingForm = form.save()
                agent.specialties.add(savingForm)
                return redirect(url)
            else:
                messages.error(request, "Don't Mess")

    context = {"agent": agent, "Specialtiesform": form}
    return render(request, "accounts/specialties.html", context)
