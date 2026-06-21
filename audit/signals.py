from django.db.models.signals import post_save
from django.dispatch import receiver

from complaint.models import Complaint
from .models import AuditLog

@receiver(post_save, sender=Complaint)
def Complaint_audit(sender, instance, created, **kwargs):

    action = "Created" if created else "Updated"

    AuditLog.objects.create(
        user=None,
        action=action,
        model_name="Complaint",
        object_id=instance.Complaint_id
    )
    
