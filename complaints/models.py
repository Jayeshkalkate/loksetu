import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.pdf', '.mp4'}
MAX_UPLOAD = 10 * 1024 * 1024


def validate_upload(f):
    if os.path.splitext(f.name)[1].lower() not in ALLOWED_EXT:
        raise ValidationError('Allowed files: JPG, PNG, PDF, MP4.')
    if f.size > MAX_UPLOAD:
        raise ValidationError('File is larger than 10 MB.')


class Status(models.TextChoices):
    SUBMITTED = 'SUBMITTED', 'Submitted'
    RECEIVED = 'RECEIVED', 'Received'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under review'
    NEEDS_INFO = 'NEEDS_INFO', 'More information needed'
    IN_PROGRESS = 'IN_PROGRESS', 'In progress'
    RESOLVED = 'RESOLVED', 'Resolved'
    CLOSED = 'CLOSED', 'Closed'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey('departments.Department', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Complaint(models.Model):
    complaint_id = models.CharField(max_length=24, unique=True, null=True, editable=False)
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    department = models.ForeignKey('departments.Department', on_delete=models.PROTECT, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    district = models.ForeignKey('departments.District', on_delete=models.PROTECT)
    taluka = models.CharField(max_length=100, blank=True)
    village_city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    incident_date = models.DateField(default=timezone.localdate)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=14, choices=Status.choices, default=Status.SUBMITTED)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='assigned_complaints')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.complaint_id or self.title

    def save(self, *a, **k):
        self.department = self.category.department  # automatic department routing
        super().save(*a, **k)
        if not self.complaint_id:
            self.complaint_id = f'LKS-MH-{timezone.now().year}-{self.pk:06d}'
            super().save(update_fields=['complaint_id'])

    def record(self, by, note=''):
        """Log the current status: timeline entry, citizen notification, audit record."""
        from audit.models import log
        from notifications.models import Notification
        StatusHistory.objects.create(complaint=self, status=self.status, note=note, changed_by=by)
        Notification.objects.create(user=self.citizen,
                                    message=f'{self.complaint_id}: {self.get_status_display()}')
        log(by, 'Complaint status', self.complaint_id, new=self.status)
        if self.citizen.email:
            send_mail(f'LOKSETU {self.complaint_id}: {self.get_status_display()}',
                      f'Your complaint "{self.title}" is now: {self.get_status_display()}.\n'
                      f'Track it with ID {self.complaint_id}.', None, [self.citizen.email], fail_silently=True)

    def set_status(self, status, by, note=''):
        self.status = status
        self.save(update_fields=['status', 'updated'])
        self.record(by, note)


class Evidence(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to='evidence/%Y/%m/', validators=[validate_upload])
    uploaded = models.DateTimeField(auto_now_add=True)


class StatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=14, choices=Status.choices)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['at']
