from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        OFFICER = 'OFFICER', 'Officer'
        DEPT_ADMIN = 'DEPT_ADMIN', 'Department Administrator'
        SUPER = 'SUPER', 'Super Administrator'

    role = models.CharField(max_length=12, choices=Role.choices, default=Role.CITIZEN)
    mobile = models.CharField(max_length=15, blank=True)
    district = models.ForeignKey('departments.District', null=True, blank=True, on_delete=models.SET_NULL)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL,
                                   help_text='For officers and department administrators')
