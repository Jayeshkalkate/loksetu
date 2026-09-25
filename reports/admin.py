from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'report_type', 'published')
    list_filter = ('report_type', 'department')
    search_fields = ('title', 'summary')
