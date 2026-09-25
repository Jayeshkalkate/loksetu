from django.contrib import admin

from .models import Fund


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'financial_year', 'allocated_crore', 'utilized_crore', 'updated')
    list_filter = ('financial_year', 'department')
    search_fields = ('name', 'description')
