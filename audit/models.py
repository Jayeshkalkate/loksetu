from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=255)

    model_name = models.CharField(max_length=100)

    object_id = models.CharField(max_length=100)

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.action}"