from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import *
from accounts.forms import *


def index(request):
    users = User.objects.all()
    datas = {
        "pk": 2,
        "fields": {
            "password": "pbkdf2_sha256$720000$HgxoAIQk66Hiorc1FnSotm$TDZFrHPDEwLl7L7uX+4nsrqi7oY3GQzlwLDfDlIq6bM=",
            "first_name": "Sara",
            "last_name": "Martinez",
            "email": "admin@gmail.com",
            "username": "Sara Martinez",
            "job_title": "Senior Real Estate Advisor",
            "job_des": "Helping you find not just a house",
            "image": "UserImages/agent-3.webp",
            "phone": "+201099999999",
            "about_me": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.",
            "my_approach": "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.",
            "office": "Giza, Haram, Street1, 6th Floor",
            "graduation": 1,
            "linkedin": "http://Linkedin.com",
            "facebook": "http://Facebook.com",
            "instagram": "http://Instagram.com",
            "is_active": True,
            "is_staff": True,
            "is_admin": True,
            "is_superuser": True,
            "date_joined": "2025-09-22T00:56:52.836Z",
            "last_login": "2025-09-22T01:15:26.995Z",
            "groups": [],
            "user_permissions": [],
            "certifications": [1],
            "specialties": [8, 7, 6, 5, 2],
            "recentachievement": [5, 4],
        },
    }
    return render(request, "accounts/index.html", {"users": users})


def agent_detail(request, username):
    agent = get_object_or_404(User, username=username)
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reForm = form.save(commit=False)
            reForm.user = agent
            if reForm.is_available():
                
                reForm.save()
                print("success")
            else:
                print("this time is already booked ")

    else:
        form = ReservationForm()
    return render(request, "accounts/agent.html", {"agent": agent, "form": form})
