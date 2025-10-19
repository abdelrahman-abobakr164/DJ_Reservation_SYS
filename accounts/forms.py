from django import forms
from core.models import *
from accounts.models import *
from django.contrib.auth import get_user_model


User = get_user_model()


DAYS_OF_WEEK = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)


class UserForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "image",
            "job_title",
            "job_des",
            "office",
            "number_of_reservations",
            "booking_duration",
            "about_me",
            "my_approach",
            "linkedin",
            "instagram",
            "facebook",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].widget.attrs["placeholder"] = field.capitalize().replace(
                "_", " "
            )
        self.fields["username"].label = "Full Name"


class WorkingTimesForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(required=True, choices=DAYS_OF_WEEK)
    start_time = forms.TimeField(
        required=True, widget=forms.TimeInput(attrs={"type": "time"})
    )
    end_time = forms.TimeField(
        required=True, widget=forms.TimeInput(attrs={"type": "time"})
    )

    class Meta:
        model = ELDay
        fields = ["day_of_week", "start_time", "end_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class GraduationForm(forms.ModelForm):
    title = forms.CharField(
        label="Name",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}))

    class Meta:
        model = Graduation
        fields = ["title", "image"]


class CertificationsForm(forms.ModelForm):
    title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}))

    class Meta:
        model = Certification
        fields = ["title", "image"]


class SpecialtiesForm(forms.ModelForm):
    title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Specialtie
        fields = ["title"]


class RecentAchievementsForm(forms.ModelForm):
    title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = RecentAchievement
        fields = ("title",)
