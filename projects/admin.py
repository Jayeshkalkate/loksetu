from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'district', 'status', 'budget_crore', 'updated')
    list_filter = ('status', 'department', 'district')
    search_fields = ('name', 'description')
