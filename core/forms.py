from django import forms
from core.models import *
from datetime import date
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField


User = get_user_model()


class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat()}),
    )
    time = forms.TimeField(
        required=True, widget=forms.TimeInput(attrs={"type": "time"})
    )
    phone = PhoneNumberField()

    class Meta:
        model = Reservation
        fields = [
            "full_name",
            "email",
            "phone",
            "subject",
            "date",
            "time",
        ]

    def __init__(self, *args, agent=None, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["full_name"].widget.attrs["placeholder"] = "Full Name"
        self.fields["email"].widget.attrs["placeholder"] = "Email Address"
        self.fields["email"].help_text = (
            "Write a Right Email Address Because I Will Contact To You"
        )
        self.fields["phone"].widget.attrs["placeholder"] = "+20xxxxxxxxxx"

        if agent:
            user = User.objects.get(username=agent.username)
            if user.number_of_reservations == user.appointments:
                self.fields["date"].widget.attrs["min"] = (
                    date.today() + timedelta(days=1)
                ).isoformat()

    def clean(self):
        clean_data = super().clean()
        time = self.cleaned_data.get("time")
        date = self.cleaned_data.get("date")
        if date and time:
            if date < date.today():
                raise forms.ValidationError("Cannot Make Reservations for Past Dates.")
        return clean_data
