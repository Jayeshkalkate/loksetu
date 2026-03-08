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


class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Taluka(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Village(models.Model):
    taluka = models.ForeignKey(Taluka, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('state_admin', 'State Admin'),
        ('district_admin', 'District Admin'),
        ('taluka_admin', 'Taluka Admin'),
        ('village_admin', 'Village Admin'),
        ('citizen', 'Citizen'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    taluka = models.ForeignKey(Taluka, on_delete=models.SET_NULL, null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"