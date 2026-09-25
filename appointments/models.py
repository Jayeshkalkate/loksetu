from django.conf import settings
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    appointment_id = models.CharField(max_length=24, unique=True, null=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL,
                                    help_text='Which department you want to meet')
    purpose = models.CharField(max_length=200)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    officer_remarks = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.appointment_id or self.purpose

    def save(self, *a, **k):
        super().save(*a, **k)
        if not self.appointment_id:
            self.appointment_id = f'LKS-APT-{timezone.now().year}-{self.pk:05d}'
            super().save(update_fields=['appointment_id'])
