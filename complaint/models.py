from django.db import models
from django.conf import settings
import datetime
from django.contrib.auth.models import User

class Complaint(models.Model):

    Complaint_id = models.CharField(max_length=20, unique=True, blank=True)

    # Citizen Info
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)

    gender = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12, blank=True, null=True)

    # Address
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    ward = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)

    # Complaint Info
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()

    issue_location = models.CharField(max_length=200)
    issue_date = models.DateField()

    evidence = models.FileField(upload_to='Complaint/', blank=True, null=True)

    # Map Location
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Status
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    
    # NEW FIELD
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.Complaint_id:

            year = datetime.datetime.now().year
            count = Complaint.objects.count() + 1

            self.Complaint_id = f"LKS-MH-{year}-{count:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.Complaint_id
    

class ComplaintHistory(models.Model):

    Complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="history"
    )

    status = models.CharField(max_length=50)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Complaint.Complaint_id} - {self.status}"