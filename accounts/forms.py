from django import forms
from datetime import date, time
from .models import Reservation
from phonenumber_field.formfields import PhoneNumberField


class ReservationForm(forms.ModelForm):
    retime = forms.TimeField(
        label="Time", required=True, widget=forms.TimeInput(attrs={"type": "time"})
    )
    redate = forms.DateField(
        label="Date",
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat()}),
    )
    phone = PhoneNumberField(required=True)

    class Meta:
        model = Reservation
        fields = [
            "full_name",
            "email",
            "phone",
            "subject",
            "redate",
            "retime",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["full_name"].widget.attrs["placeholder"] = "Full Name"
        self.fields["email"].widget.attrs["placeholder"] = "Email Address"
        self.fields["phone"].widget.attrs["placeholder"] = "+20xxxxxxxxxx"

    def clean(self):
        clean_data = super().clean()
        redate = self.cleaned_data.get("redate")
        retime = self.cleaned_data.get("retime")
        if redate and retime:
            if redate < date.today():
                raise forms.ValidationError("Cannot Make Reservations for Past Dates.")
            if retime < time(9, 0) and retime > time(21, 0):
                print(retime)
                raise forms.ValidationError(
                    "Reservations Must be Between 9:00 AM and 9:00 PM."
                )
        return clean_data
