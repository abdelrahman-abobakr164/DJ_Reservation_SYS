from datetime import date
from celery import shared_task
from django.conf import settings
from .models import Reservation
from django.core.mail import EmailMessage

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
                email = EmailMessage(
                    subject=f"Your {reservation.subject} With {reservation.agent}",
                    body=f"Your {reservation.subject} With {reservation.agent} is Today At {reservation.time} Don't Forget",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[reservation.email],
                    reply_to=[reservation.agent.email],
                )
                email.send()
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
def send_email_to_users(subject, message, from_agent, to_user):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_user],
        reply_to=[from_agent],
    )
    email.send()
