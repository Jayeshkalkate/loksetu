from django.contrib.auth.models import AbstractUser
from django.db import models

STAFF_ROLES = ('OFFICER', 'DEPT_ADMIN', 'SUPER')


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

    def save(self, *a, **k):
        if self.role in STAFF_ROLES:
            self.is_staff = True  # officers/admins must be able to sign in to /admin/
        super().save(*a, **k)
        self.sync_groups()

    def sync_groups(self):
        """Give staff roles the matching permission group (created after each migrate)."""
        from django.contrib.auth.models import Group
        wanted = {'OFFICER': 'Officers', 'DEPT_ADMIN': 'Department Admins', 'SUPER': 'Department Admins'}
        managed = Group.objects.filter(name__in=set(wanted.values()))
        target = managed.filter(name=wanted.get(self.role)).first()
        for g in managed:
            if g == target:
                self.groups.add(g)
            else:
                self.groups.remove(g)
