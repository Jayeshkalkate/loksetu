from django.db import models
from django.contrib.auth.models import User

class Citizen(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12, null=True, blank=True)

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
    
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('state_admin', 'State Admin'),
        ('citizen', 'Citizen'),
        )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"