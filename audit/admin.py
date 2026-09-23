from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "model_name",
        "object_id",
        "ip_address",
    )
    list_filter = ("action", "model_name", "timestamp", "user")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "model_name",
        "object_id",
        "ip_address",
        "changes",
    )
    date_hierarchy = "timestamp"
    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "changes",
        "ip_address",
        "user_agent",
        "request_path",
        "timestamp",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        """Disallow manual creation of audit logs via admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disallow editing of existing audit logs."""
        return False

    def get_readonly_fields(self, request, obj=None):
        # All fields are readonly
        return self.readonly_fields