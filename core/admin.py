from django.contrib import admin
from .models import *

# Register your models here.


class ELDayAdmin(admin.ModelAdmin):
    list_display = ["agent", "day_of_week", "start_time", "end_time"]
    search_fields = ("agent",)
    list_display_links = ["agent"]


class ReservationAdmin(admin.ModelAdmin):
    list_display = ["agent", "full_name", "date", "time", "status"]
    list_editable = ("status",)
    list_display_links = ["agent"]


admin.site.register(ELDay, ELDayAdmin)
admin.site.register(Reservation, ReservationAdmin)
