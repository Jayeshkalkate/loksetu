from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Citizen(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    phone = models.CharField(max_length=10, unique=True)
    aadhaar = models.CharField(max_length=12, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['district']),
            models.Index(fields=['taluka']),
            ]

    gender = models.CharField(max_length=10)
    
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    ward = models.CharField(max_length=20)

    pincode = models.CharField(max_length=6)

    address = models.TextField()

    def __str__(self):
        return self.user.username


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('village_officer', 'Village Officer'),
        ('taluka_officer', 'Taluka Officer'),
        ('district_officer', 'District Officer'),
        ('state_officer', 'State Officer'),
        ('super_admin', 'Super Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')

    def __str__(self):
        return f"{self.user.username} ({self.role})"