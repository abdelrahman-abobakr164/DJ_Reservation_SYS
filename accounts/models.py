from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
from core.models import ELDay

BOOKING_DURATION = (
    (1, "1/2 Hour"),
    (2, "1 Hour"),
    (3, "2 Hours"),
    (4, "3 Hours"),
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
    job_title = models.CharField(max_length=50, blank=True)
    job_des = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to="UserImages/", blank=True)
    phone = PhoneNumberField(region="EG", blank=True)
    about_me = models.TextField(blank=True)
    my_approach = models.TextField(blank=True)
    office = models.CharField(max_length=200, blank=True)
    number_of_reservations = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)], null=True, blank=True
    )
    appointments = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    booking_duration = models.IntegerField(choices=BOOKING_DURATION)
    working_hours = models.ManyToManyField(ELDay, blank=True)
    graduation = models.ManyToManyField("Graduation", blank=True)
    certifications = models.ManyToManyField("Certification", blank=True)
    specialties = models.ManyToManyField("Specialtie", blank=True)
    recent_achievements = models.ManyToManyField("RecentAchievement", blank=True)

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


class Certification(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="UserImages/", null=True, blank=True)

    def __str__(self):
        return self.title


class Graduation(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="UserImages/", null=True, blank=True)

    def __str__(self):
        return self.title


class Specialtie(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class RecentAchievement(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title
