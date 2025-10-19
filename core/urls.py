from django.urls import path
from . import views


urlpatterns = [
    path("", views.agents, name="agents"),
    path("agent-<str:username>", views.agent_detail, name="agent_detail"),
    path(
        "agent-<str:username>'s/scheduled-reservations",
        views.scheduled_reservations,
        name="scheduled-reservations",
    ),
    path(
        "agent-<str:username>'s/reservations",
        views.reservations_list,
        name="reservations",
    ),
]
