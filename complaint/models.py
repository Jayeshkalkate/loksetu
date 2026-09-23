import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from utils.encrypted_fields import EncryptedCharField, mask_aadhaar

User = get_user_model()


class Complaint(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
        ("Closed", "Closed"),
    ]

    complaint_id = models.CharField(max_length=20, unique=True, blank=True)

    # Citizen Info
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10)
    # Encrypted at rest — see utils/encrypted_fields.py. Use masked_aadhaar
    # for display; never log the raw value.
    aadhaar = EncryptedCharField(max_length=12, blank=True, null=True)

    # Address
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    ward = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)

    # Complaint details
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_location = models.CharField(max_length=200)
    issue_date = models.DateField()
    evidence = models.FileField(upload_to='complaints/%Y/%m/%d/', blank=True, null=True)

    # Map Location
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['complaint_id']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['district']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            # Generate a unique ID (LKS-MH-XXXXXXXX), retrying on the rare
            # collision instead of trusting uuid4 uniqueness blindly.
            for _ in range(5):
                candidate = f"LKS-MH-{uuid.uuid4().hex[:8].upper()}"
                if not Complaint.objects.filter(complaint_id=candidate).exists():
                    self.complaint_id = candidate
                    break
            else:
                self.complaint_id = f"LKS-MH-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def masked_aadhaar(self):
        return mask_aadhaar(self.aadhaar)

    def __str__(self):
        return self.complaint_id


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="history"
    )
    status = models.CharField(max_length=50)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.status} at {self.timestamp}"