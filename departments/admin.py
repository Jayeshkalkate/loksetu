from django.contrib import admin
from .models import Department, DepartmentOfficer, District


class DepartmentOfficerInline(admin.TabularInline):
    model = DepartmentOfficer
    extra = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'scheme_count', 'officer_count', 'last_verified')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'responsibilities')
    inlines = [DepartmentOfficerInline]
    fieldsets = (
        (None, {'fields': ('name', 'category', 'description', 'responsibilities')}),
        ('Contact directory', {'fields': ('hod_name', 'hod_designation', 'phone', 'email', 'address', 'website')}),
        ('Citizen help', {'fields': ('citizen_helpline', 'grievance_officer', 'grievance_portal_url',
                                     'rti_officer', 'rti_appellate_authority')}),
        ('Sourcing', {'fields': ('source_url', 'last_verified')}),
    )


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'headquarters', 'population', 'talukas', 'villages')
    list_filter = ('division',)
    search_fields = ('name', 'division')
