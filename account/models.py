from django.db import models
from django.contrib.auth.models import User

class Citizen(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12, null=True, blank=True)

    gender = models.CharField(max_length=10)

    ward = models.CharField(max_length=20)
    village = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)

    address = models.TextField()

    def __str__(self):
        return self.user.username
