from datetime import date
from celery import shared_task
from .models import Reservation
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_reservations_emails():
    try:
        cancelled_count = Reservation.objects.filter(
            date__lt=date.today(), status="Pending"
        ).update(status="Cancelled")

        remind_email = Reservation.objects.filter(date=date.today(), status="Confirmed")

        emails_count = 0
        failed_emails = 0

        for reservation in remind_email:
            try:
                send_mail(
                    subject=f"Your {reservation.subject} With {reservation.agent}",
                    message=f"Your {reservation.subject} With {reservation.agent} is Today At {reservation.time} Don't Forget",
                    from_email=reservation.agent.email,
                    recipient_list=[reservation.email],
                    fail_silently=False,
                )
                emails_count += 1
            except Exception as e:
                failed_emails += 1
                logger.error(
                    f"Failed to send email for reservation {reservation.id}: {e}"
                )

        logger.info(
            f"Reservation update completed: "
            f"{cancelled_count} cancelled, "
            f"{emails_count} emails sent, "
            f"{failed_emails} failed emails"
        )

        return {
            "cancelled_count": cancelled_count,
            "emails_sent": emails_count,
            "failed_emails": failed_emails,
        }

    except Exception as e:
        logger.error(f"Reservation update task failed: {e}")
        raise


@shared_task
def send_email_to_users(subject, message, from_email, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[recipient_list],
        fail_silently=False,
    )
