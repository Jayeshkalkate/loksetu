from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import complaint
from utils.email_service import (
    send_complaint_created_email,
    send_complaint_resolved_email
)


@receiver(post_save, sender=complaint)
def complaint_email_handler(sender, instance, created, **kwargs):

    if created:
        send_complaint_created_email(instance)

    elif instance.status == "Resolved":
        send_complaint_resolved_email(instance)