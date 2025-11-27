from .models import Reservation


def navbar(request):
    if "admin" in request.path:
        return {}
    else:
        reservations_count = 0
        if request.user.is_authenticated:
            reservations_count = Reservation.objects.filter(
                agent=request.user, status="Pending"
            ).select_related('agent').count()
        return {"reservations_count": reservations_count}
