from django.urls import path
from .views import *


urlpatterns = [
    path("<str:username>'s-account", edit, name="account"),
    path("<str:username>'s-working-times", working_times, name="working-times"),
    path("<str:username>'s-graduations", graduations, name="graduations"),
    path(
        "<str:username>'s-recent_achievements",
        recent_achievements,
        name="recent_achievements",
    ),
    path("<str:username>'s-specialties", specialties, name="specialties"),
    path("<str:username>'s-certifications", certifications, name="certifications"),
]
