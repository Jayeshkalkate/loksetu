from django.contrib import admin
from .models import Complaint, ComplaintHistory


class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('status', 'updated_by', 'timestamp')
    can_delete = False


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'complaint_id', 'title', 'department', 'district',
        'status', 'is_read', 'created_at'
    )
    list_filter = ('status', 'department', 'district', 'is_read')
    search_fields = (
        'complaint_id', 'title', 'description',
        'full_name', 'phone', 'email'
    )
    readonly_fields = ('complaint_id', 'created_at', 'updated_at')
    inlines = [ComplaintHistoryInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('Complaint ID', {'fields': ('complaint_id',)}),
        ('Citizen Information', {'fields': ('full_name', 'phone', 'email', 'gender', 'aadhaar')}),
        ('Address', {'fields': ('state', 'district', 'taluka', 'village', 'ward', 'pincode')}),
        ('Complaint Details', {'fields': ('department', 'title', 'description', 'issue_location', 'issue_date', 'evidence')}),
        ('Location (Map)', {'fields': ('latitude', 'longitude')}),
        ('Status', {'fields': ('status', 'is_read')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status', 'updated_by', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('complaint__complaint_id', 'updated_by__username')
    readonly_fields = ('complaint', 'status', 'updated_by', 'timestamp')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False