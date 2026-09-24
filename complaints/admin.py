from django.contrib import admin

from accounts.models import User
from .models import Category, Complaint, Evidence, Status, StatusHistory


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ('file', 'uploaded')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class HistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('status', 'note', 'changed_by', 'at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


def _is_super(u):
    return u.is_superuser or u.role == 'SUPER'


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'department', 'district', 'status', 'assigned_to', 'created')
    list_filter = ('status', 'department', 'district')
    search_fields = ('complaint_id', 'title')
    list_select_related = ('department', 'district', 'assigned_to')
    date_hierarchy = 'created'
    inlines = [EvidenceInline, HistoryInline]
    actions = ['mark_in_progress', 'mark_resolved']

    def get_queryset(self, request):
        qs, u = super().get_queryset(request), request.user
        if _is_super(u):
            return qs
        if u.role == 'DEPT_ADMIN':
            return qs.filter(department=u.department) if u.department_id else qs.none()
        if u.role == 'OFFICER':
            return qs.filter(assigned_to=u)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        base = ['complaint_id']
        if _is_super(request.user):
            return base
        # Staff may only work the case (status / assignment), never rewrite what the citizen filed.
        locked = [f.name for f in Complaint._meta.fields
                  if f.name not in ('status', 'assigned_to') and f.editable]
        if request.user.role == 'OFFICER':
            locked.append('assigned_to')
        return base + locked

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to':
            qs = User.objects.filter(role='OFFICER', is_active=True)
            if not _is_super(request.user) and request.user.department_id:
                qs = qs.filter(department=request.user.department)
            kwargs['queryset'] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and ('status' in form.changed_data or 'assigned_to' in form.changed_data):
            obj.record(request.user, 'Updated by department')

    def _bulk(self, request, queryset, status, label):
        n = 0
        for c in queryset.exclude(status=status):
            c.set_status(status, request.user, f'Marked {label} by department')
            n += 1
        self.message_user(request, f'{n} complaint(s) marked {label}.')

    @admin.action(description='Mark selected as In progress')
    def mark_in_progress(self, request, queryset):
        self._bulk(request, queryset, Status.IN_PROGRESS, 'in progress')

    @admin.action(description='Mark selected as Resolved')
    def mark_resolved(self, request, queryset):
        self._bulk(request, queryset, Status.RESOLVED, 'resolved')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
