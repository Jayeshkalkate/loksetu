from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from audit.models import AuditLog
from audit.threadlocal import get_current_user, get_current_request
from .models import Post


def _get_audit_context():
    user = get_current_user()
    request = get_current_request()
    ip = request.META.get('REMOTE_ADDR') if request else None
    ua = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
    path = request.path[:255] if request else ''
    return user, ip, ua, path


@receiver(post_save, sender=Post)
def post_audit(sender, instance, created, **kwargs):
    user, ip, ua, path = _get_audit_context()
    AuditLog.log(
        user=user,
        action='CREATE' if created else 'UPDATE',
        model='Post',
        object_id=str(instance.id),
        changes={'title': instance.title},
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )


@receiver(post_delete, sender=Post)
def post_delete_audit(sender, instance, **kwargs):
    user, ip, ua, path = _get_audit_context()
    AuditLog.log(
        user=user,
        action='DELETE',
        model='Post',
        object_id=str(instance.id),
        changes={'title': instance.title},
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )