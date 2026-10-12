from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.db import transaction

from audit.models import log
from notifications.models import Notification
from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'subject', 'user', 'status', 'created')
    list_filter = ('status',)
    search_fields = ('ticket_id', 'subject', 'message', 'user__username')
    readonly_fields = ('ticket_id', 'user', 'subject', 'message', 'created', 'updated')
    fields = ('ticket_id', 'user', 'subject', 'message', 'status', 'response', 'created', 'updated')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Support messages can contain personal account information; only global admins see them.
        if request.user.is_superuser or request.user.role == 'SUPER':
            return qs
        return qs.none()

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and (set(form.changed_data) & {'status', 'response'}):
            Notification.objects.create(
                user=obj.user,
                message=f'{obj.ticket_id}: support ticket updated. Current status: {obj.get_status_display()}.',
            )
            log(request.user, 'Support ticket updated', obj.ticket_id,
                new=f'{obj.status}; response updated' if 'response' in form.changed_data else obj.status)
            if obj.user.email:
                subject = f'LOKSETU {obj.ticket_id}: support ticket updated'
                body = (f'Your support ticket {obj.ticket_id} has been updated.\n'
                        f'Status: {obj.get_status_display()}.\n')
                if obj.response:
                    body += f'Response: {obj.response}\n'
                transaction.on_commit(lambda: send_mail(
                    subject, body, settings.DEFAULT_FROM_EMAIL, [obj.user.email], fail_silently=True))
