import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from complaint.models import Complaint
from .models import AuditLog
from .threadlocal import get_current_user, get_current_request

logger = logging.getLogger(__name__)


def _get_request_context():
    """Helper to fetch user and request details from thread-local storage."""
    user = get_current_user()
    request = get_current_request()
    ip = None
    ua = ""
    path = ""
    if request:
        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT", "")[:255]
        path = request.path[:255]
    return user, ip, ua, path


@receiver(post_save, sender=Complaint)
def complaint_post_save(sender, instance, created, **kwargs):
    """
    Log creation/update of a Complaint.
    """
    user, ip, ua, path = _get_request_context()
    action = "CREATE" if created else "UPDATE"

    # For updates, capture changed fields (only if we have a previous version)
    changes = None
    if not created:
        # We could use a diff library, but for simplicity we store a placeholder
        # You can extend this to capture actual changes using a pre_save signal
        # or by comparing with a snapshot.
        changes = {"info": "Object updated"}

    AuditLog.log(
        user=user,
        action=action,
        model="Complaint",
        object_id=instance.complaint_id,
        changes=changes,
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )


@receiver(post_delete, sender=Complaint)
def complaint_post_delete(sender, instance, **kwargs):
    """
    Log deletion of a Complaint.
    """
    user, ip, ua, path = _get_request_context()
    AuditLog.log(
        user=user,
        action="DELETE",
        model="Complaint",
        object_id=instance.complaint_id,
        changes={"deleted_at": str(instance.created_at)},  # optional info
        ip_address=ip,
        user_agent=ua,
        request_path=path,
    )


# Add more receivers here for other models as needed.
# Example:
# @receiver(post_save, sender=Scheme)
# def scheme_post_save(sender, instance, created, **kwargs):
#     ...