from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from utils.encrypted_fields import EncryptedCharField, mask_aadhaar


class Citizen(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, unique=True)
    # Aadhaar is sensitive national-ID PII — encrypted at rest (see
    # utils/encrypted_fields.py). Never log or display the raw value;
    # use mask_aadhaar() for anything shown in the UI.
    aadhaar = EncryptedCharField(max_length=12, null=True, blank=True)
    gender = models.CharField(max_length=10)
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)
    address = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["district"]),
            models.Index(fields=["taluka"]),
            models.Index(fields=["village"]),
        ]

    @property
    def masked_aadhaar(self):
        return mask_aadhaar(self.aadhaar)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone})"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("citizen", "Citizen"),
        ("village_officer", "Village Officer"),
        ("taluka_officer", "Taluka Officer"),
        ("district_officer", "District Officer"),
        ("state_officer", "State Officer"),
        ("super_admin", "Super Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="citizen")

    # Jurisdiction assignment for officers, so district/taluka/village
    # dashboards can be scoped to the area an officer is actually
    # responsible for instead of showing nothing.
    assigned_district = models.CharField(max_length=100, blank=True, null=True)
    assigned_taluka = models.CharField(max_length=100, blank=True, null=True)
    assigned_village = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["assigned_district"]),
            models.Index(fields=["assigned_taluka"]),
            models.Index(fields=["assigned_village"]),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.role})"
