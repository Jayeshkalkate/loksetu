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
        # Revoke stale admin flags when a privileged role is demoted.
        # Otherwise changing the role alone could leave admin access behind.
        old_staff, old_superuser = self.is_staff, self.is_superuser
        previous_role = None
        if self.pk:
            previous_role = type(self).objects.filter(pk=self.pk).values_list('role', flat=True).first()
        if previous_role in STAFF_ROLES and self.role not in STAFF_ROLES:
            self.is_staff = False
        if previous_role == self.Role.SUPER and self.role != self.Role.SUPER:
            self.is_superuser = False
        if self.role in STAFF_ROLES:
            self.is_staff = True  # officers/admins must be able to sign in to /admin/
        if self.role == self.Role.SUPER:
            # Keep the application role and Django's global admin flag consistent.
            self.is_superuser = True
            self.is_staff = True
        # Honour partial saves while ensuring role-driven privilege changes reach the DB.
        changed_flags = set()
        if self.is_staff != old_staff:
            changed_flags.add('is_staff')
        if self.is_superuser != old_superuser:
            changed_flags.add('is_superuser')
        if changed_flags and k.get('update_fields') is not None:
            k['update_fields'] = set(k['update_fields']) | changed_flags
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

