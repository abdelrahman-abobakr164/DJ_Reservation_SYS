from django.db import models
from django.conf import settings
from datetime import datetime, timedelta, time
from django.db.models import Q, UniqueConstraint
from phonenumber_field.modelfields import PhoneNumberField

DAYS_OF_WEEK = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)

SUBJECT = (
    ("Detection", "Detection"),
    ("Consultation", "Consultation"),
    ("Interview", "Interview"),
    ("Submiting an Application", "Submiting an Application"),
)

STATUS = (
    ("Pending", "Pending"),
    ("Confirmed", "Confirmed"),
    ("Cancelled", "Cancelled"),
)


class ELDay(models.Model):
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(21, 0))

    class Meta:
        ordering = ("day_of_week",)
        constraints = [
            UniqueConstraint(
                fields=["agent", "day_of_week", "start_time", "end_time"],
                name="Unique_agent_working_times",
            )
        ]

    def __str__(self):
        return f"{self.day_of_week} from {self.start_time} to {self.end_time}"

    def get_working_hours(self):
        return (self.start_time, self.end_time)


class Reservation(models.Model):
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=250)
    phone = PhoneNumberField(region="EG")
    subject = models.CharField(max_length=100, choices=SUBJECT)
    date = models.DateField()
    time = models.TimeField(null=True)
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("date",)
        constraints = [
            UniqueConstraint(
                fields=["agent", "time", "date"],
                condition=Q(status__in=["Pending", "Confirmed"]),
                name="Unique_agent_date_time",
            )
        ]

    def __str__(self):
        return f"{self.full_name} with {self.agent.get_fullname()} - {self.date} {self.time}"

    def is_available(self):
        time_duration = (
            timedelta(hours=1)
            if self.agent.booking_duration != 1
            else timedelta(minutes=30)
        )

        HourLater = (
            datetime.combine(datetime.today(), self.time) + time_duration
        ).time()
        HourEarlier = (
            datetime.combine(datetime.today(), self.time) - time_duration
        ).time()

        conflicting_reservations = (
            Reservation.objects.filter(
                agent=self.agent,
                date=self.date,
                status__in=["Pending", "Confirmed"],
            )
            .filter(
                Q(time__gte=self.time, time__lt=HourLater)
                | Q(time__lte=self.time, time__gt=HourEarlier)
            )
            .exclude(id=self.id)
        )

        return not conflicting_reservations.exists()
