from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "phone",
        "job_title",
        "number_of_reservations",
        "booking_duration",
    ]
    list_display_links = ["email", "username"]


class ContactAdmin(admin.ModelAdmin):
    list_display = ["email"]
    list_display_links = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(Graduation)
admin.site.register(Certification)
admin.site.register(Specialtie)
admin.site.register(RecentAchievement)
