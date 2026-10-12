from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.db import transaction

from audit.models import log
from notifications.models import Notification
from .models import Appointment


def _is_super(user):
    return user.is_superuser or user.role == 'SUPER'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'user', 'department', 'preferred_date', 'preferred_time', 'status')
    list_filter = ('status', 'department')
    search_fields = ('appointment_id', 'user__username', 'purpose')
    list_select_related = ('user', 'department')
    autocomplete_fields = ['user']
    readonly_fields = ('appointment_id', 'created', 'updated')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _is_super(request.user):
            return qs
        if request.user.role in ('OFFICER', 'DEPT_ADMIN') and request.user.department_id:
            return qs.filter(department_id=request.user.department_id)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        if _is_super(request.user):
            return ('appointment_id', 'created', 'updated')
        # Department staff can only update the workflow, never rewrite a citizen's request.
        return tuple(f.name for f in self.model._meta.fields
                     if f.name not in ('id', 'status', 'officer_remarks'))

    def has_add_permission(self, request):
        # Appointments must originate from the citizen's authenticated account.
        return _is_super(request.user)

    def has_delete_permission(self, request, obj=None):
        return _is_super(request.user)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and (set(form.changed_data) & {'status', 'officer_remarks'}):
            status_label = obj.get_status_display()
            Notification.objects.create(
                user=obj.user,
                message=f'{obj.appointment_id}: appointment updated. Current status: {status_label}.',
            )
            log(request.user, 'Appointment updated', obj.appointment_id,
                new=f'{obj.status}; remarks updated' if 'officer_remarks' in form.changed_data else obj.status)
            if obj.user.email:
                subject = f'LOKSETU {obj.appointment_id}: appointment updated'
                body = (f'Your appointment request {obj.appointment_id} has been updated.\n'
                        f'Status: {status_label}.\n')
                if obj.officer_remarks:
                    body += f'Officer remarks: {obj.officer_remarks}\n'
                transaction.on_commit(lambda: send_mail(
                    subject, body, settings.DEFAULT_FROM_EMAIL, [obj.user.email], fail_silently=True))
