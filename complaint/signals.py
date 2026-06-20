from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.email_service import (
    send_complaint_created_email,
    send_complaint_resolved_email
)

from complaint.models import Complaint
from audit.models import AuditLog


@receiver(post_save, sender=Complaint)
def complaint_audit(sender, instance, created, **kwargs):

    if created:
        send_complaint_created_email(instance)

    elif instance.status == "Resolved":
        send_complaint_resolved_email(instance)