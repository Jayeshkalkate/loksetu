from django.contrib import admin
from .models import *
# from .models import CustomUser

@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'total_amount', 'released_amount', 'year', 'location')
    search_fields = ('title', 'department')
    list_filter = ('year', 'location')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'status', 'used_amount')
    list_filter = ('status',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'parent')

# admin.site.register(CustomUser)
admin.site.register(Proof)
admin.site.register(Complaint)