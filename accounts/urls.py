from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("agent-<str:username>", views.agent_detail, name="detail"),
]
