from django.conf import settings
from django.db import models
from django.utils import timezone


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    ticket_id = models.CharField(max_length=24, unique=True, null=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    response = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.ticket_id or self.subject

    def save(self, *a, **k):
        super().save(*a, **k)
        if not self.ticket_id:
            self.ticket_id = f'LKS-SUP-{timezone.now().year}-{self.pk:05d}'
            super().save(update_fields=['ticket_id'])
