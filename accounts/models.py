from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta, time

DAYCHOICE = (
    (0, "Saturday"),
    (1, "Sunday"),
    (2, "Monday"),
    (3, "tuesday"),
    (4, "thursday"),
    (5, "Wednesday"),
    (6, "Friday"),
)

SUBJECT = (
    ("Detection", "Detection"),
    ("Submiting an Application", "Submiting an Application"),
    ("Interview", "Interview"),
)


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User Must Has an Email Address")

        if not username:
            raise ValueError("User Must Has Username")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    job_title = models.CharField(max_length=50)
    job_des = models.CharField(max_length=50)
    image = models.ImageField(upload_to="UserImages/")
    phone = PhoneNumberField(region="EG")
    about_me = models.TextField()
    my_approach = models.TextField()
    office = models.CharField(max_length=200)
    number_of_reservations = models.PositiveIntegerField(default=1)
    start_time = models.TimeField(null=True, blank=True)
    endtime_time = models.TimeField(null=True, blank=True)
    graduation = models.ManyToManyField("Graduation")
    certifications = models.ManyToManyField("Certification")
    specialties = models.ManyToManyField("Specialtie")
    recentachievement = models.ManyToManyField("RecentAchievement", blank=True)

    linkedin = models.URLField(max_length=200, null=True, blank=True)
    facebook = models.URLField(max_length=200, null=True, blank=True)
    instagram = models.URLField(max_length=200, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_superuser or super().has_module_perms(app_label)

    def get_all_permissions(self, obj=None):
        if self.is_superuser:
            return set()
        return super().get_all_permissions(obj)

    def get_group_permissions(self, obj=None):
        if self.is_superuser:
            return set()
        return super().get_group_permissions(obj)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = self.phone.as_e164
        super().save(*args, **kwargs)


class WorkDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYCHOICE, unique=True)
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(21, 0))

    class Meta:
        ordering = ("day_of_week",)

    def __str__(self):
        return f"{self.get_day_of_week_display()} from {self.start_time} to {self.end_time}"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=250)
    phone = PhoneNumberField(region="EG")
    subject = models.CharField(max_length=100, choices=SUBJECT)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = ["redate", "retime"]
        ordering = ["redate", "retime"]

    def __str__(self):
        return f"{self.full_name} - {self.redate} {self.retime}"

    def is_available(self):
        conflict_date = Reservation.objects.filter(
            redate=self.redate, retime=self.retime
        ).exclude(id=self.id)
        return not conflict_date.exists()


class Certification(models.Model):
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-created_at",)


class Specialtie(models.Model):
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-created_at",)


class RecentAchievement(models.Model):
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-created_at",)


class Graduation(models.Model):
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-created_at",)
