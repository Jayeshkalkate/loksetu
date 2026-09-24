from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    object_repr = models.CharField(max_length=200, blank=True)
    old_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.created:%Y-%m-%d %H:%M} {self.action}'


def log(user, action, obj='', old='', new=''):
    AuditLog.objects.create(user=user if getattr(user, 'pk', None) else None, action=action,
                            object_repr=str(obj)[:200], old_value=str(old)[:200], new_value=str(new)[:200])
