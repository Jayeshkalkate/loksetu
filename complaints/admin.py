from django.contrib import admin
from .models import Category, Complaint, Evidence, StatusHistory


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0


class HistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('status', 'note', 'changed_by', 'at')
    can_delete = False
    def has_add_permission(self, request, obj=None): return False


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'department', 'district', 'status', 'assigned_to', 'created')
    list_filter = ('status', 'department', 'district')
    search_fields = ('complaint_id', 'title')
    readonly_fields = ('complaint_id',)
    inlines = [EvidenceInline, HistoryInline]

    def get_queryset(self, request):
        qs, u = super().get_queryset(request), request.user
        if u.is_superuser or u.role == 'SUPER':
            return qs
        if u.role == 'DEPT_ADMIN':
            return qs.filter(department=u.department)
        if u.role == 'OFFICER':
            return qs.filter(assigned_to=u)
        return qs.none()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'status' in form.changed_data or 'assigned_to' in form.changed_data:
            obj.record(request.user, 'Updated by department')


admin.site.register(Category)
