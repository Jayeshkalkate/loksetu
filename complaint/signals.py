import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from audit.threadlocal import get_current_user, get_current_request
from complaint.models import Complaint, ComplaintHistory
from audit.models import AuditLog

logger = logging.getLogger(__name__)


def _get_audit_context():
    """Get user and request from thread-local (set by AuditMiddleware)."""
    user = get_current_user()
    request = get_current_request()
    ip = request.META.get('REMOTE_ADDR') if request else None
    ua = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
    path = request.path[:255] if request else ''
    return user, ip, ua, path


@receiver(post_save, sender=Complaint)
def complaint_audit(sender, instance, created, **kwargs):
    """Log complaint creation/update to AuditLog and send email notifications."""
    user, ip, ua, path = _get_audit_context()
    action = 'CREATE' if created else 'UPDATE'
    changes = None
    if not created:
        # Could compute changes, but we'll store a simple note
        changes = {'status': instance.status, 'is_read': instance.is_read}

    AuditLog.log(
        user=user,
        action=action,
        model='Complaint',
        object_id=instance.complaint_id,
        changes=changes,
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )

    # Send email notifications (async preferred, but we'll do it in a try-except)
    if created:
        try:
            from utils.email_service import send_complaint_created_email
            send_complaint_created_email(instance)
        except Exception as e:
            logger.error(f'Failed to send complaint created email: {e}')
    elif instance.status == 'Resolved':
        try:
            from utils.email_service import send_complaint_resolved_email
            send_complaint_resolved_email(instance)
        except Exception as e:
            logger.error(f'Failed to send complaint resolved email: {e}')


@receiver(post_delete, sender=Complaint)
def complaint_delete_audit(sender, instance, **kwargs):
    """Log complaint deletion."""
    user, ip, ua, path = _get_audit_context()
    AuditLog.log(
        user=user,
        action='DELETE',
        model='Complaint',
        object_id=instance.complaint_id,
        changes={'deleted_at': str(instance.created_at)},
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )