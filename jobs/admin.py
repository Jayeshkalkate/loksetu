from django.contrib import admin
from .models import JobNotification


@admin.register(JobNotification)
class JobNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'last_date', 'published')
    list_filter = ('organization',)
    search_fields = ('title', 'organization', 'description')
