from datetime import date
from celery import shared_task
from .models import Reservation
from django.core.mail import send_mail


@shared_task
def update_shceduled_reservations():
    Reservation.objects.filter(date__lt=date.today(), status="Pending").update(
        status="Cancelled"
    )
    remind_email = Reservation.objects.filter(date=date.today(), status="Confirmed")

    for i in remind_email:
        send_mail(
            subject=f"Your {i.subject} With {i.agent}",
            message=f"it's Your {i.subject} With {i.agent} is Today At {i.time} Don't Forget ",
            from_email=i.agent.email,
            recipient_list=[i.email],
            fail_silently=False,
        )


@shared_task
def send_email_to_users(subject, message, from_email, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[recipient_list],
        fail_silently=False,
    )
