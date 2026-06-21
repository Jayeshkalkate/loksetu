from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.email_service import (
    send_Complaint_created_email,
    send_Complaint_resolved_email
)
from audit.models import AuditLog
from complaint.models import Complaint
from complaint.models import ComplaintHistory

@receiver(post_save, sender=Complaint)
def complaint_audit(sender, instance, created, **kwargs):

    if created:
        send_Complaint_created_email(instance)

    elif instance.status == "Resolved":
        send_Complaint_resolved_email(instance)
        
