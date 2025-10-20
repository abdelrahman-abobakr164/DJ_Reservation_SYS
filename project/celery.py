from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.timezone = "Africa/Cairo"

app.conf.beat_schedule = {
    "update-schedule-reservation-send-emails": {
        "task": "core.tasks.update_reservations_emails",
        "schedule": crontab(hour=6, minute=0),
    }
}
