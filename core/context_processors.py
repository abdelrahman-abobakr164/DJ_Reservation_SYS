from .models import Reservation
from django.utils import timezone


def navbar(request):
    if "superuser" in request.path:
        return {}

    reservations_count = 0
    today = timezone.now().date()

    if request.user.is_authenticated:
        reservations_count = (
            Reservation.objects.filter(
                agent=request.user, status="Pending", date__gte=today
            )
            .select_related("agent")
            .count()
        )
    return {"reservations_count": reservations_count}
