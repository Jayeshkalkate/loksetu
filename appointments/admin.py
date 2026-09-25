from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'user', 'department', 'preferred_date', 'preferred_time', 'status')
    list_filter = ('status', 'department')
    search_fields = ('appointment_id', 'user__username', 'purpose')
    autocomplete_fields = ['user']
