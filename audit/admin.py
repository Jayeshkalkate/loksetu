from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created', 'user', 'action', 'object_repr', 'old_value', 'new_value')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

    def has_module_permission(self, request):
        # AuditLog has no department scoping, so any non-superuser group with
        # view_auditlog would see every department's audit trail. Restrict this
        # to real superusers only, regardless of group permissions.
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

