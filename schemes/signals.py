import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from audit.models import AuditLog
from audit.threadlocal import get_current_user, get_current_request
from .models import Scheme

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_audit_context():
    user = get_current_user()
    request = get_current_request()
    ip = request.META.get('REMOTE_ADDR') if request else None
    ua = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
    path = request.path[:255] if request else ''
    return user, ip, ua, path


@receiver(post_save, sender=Scheme)
def scheme_audit(sender, instance, created, **kwargs):
    user, ip, ua, path = _get_audit_context()
    AuditLog.log(
        user=user,
        action='CREATE' if created else 'UPDATE',
        model='Scheme',
        object_id=instance.slug,
        changes={'title': instance.title, 'is_verified': instance.is_verified},
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )

    # Send email notification on creation (async would be better)
    if created:
        try:
            from utils.email_service import send_new_scheme_email
            # Optionally send to all users or only admins
            users = User.objects.exclude(email='')
            for user in users:
                send_new_scheme_email(user.email, instance)
        except Exception as e:
            logger.error(f"Failed to send new scheme email: {e}")


@receiver(post_delete, sender=Scheme)
def scheme_delete_audit(sender, instance, **kwargs):
    user, ip, ua, path = _get_audit_context()
    AuditLog.log(
        user=user,
        action='DELETE',
        model='Scheme',
        object_id=instance.slug,
        changes={'title': instance.title},
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )