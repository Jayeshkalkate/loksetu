import json
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AuditLog(models.Model):
    """
    Central audit log for tracking actions across the system.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text="User who performed the action (if any).",
    )
    action = models.CharField(
        max_length=50,
        help_text="Action performed, e.g. CREATE, UPDATE, DELETE, LOGIN, LOGOUT.",
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the model affected.",
    )
    object_id = models.CharField(
        max_length=100,
        help_text="Primary key of the affected object.",
    )
    changes = models.TextField(
        blank=True,
        default="",
        help_text="JSON-serialised dict of changes (field: old_value, new_value).",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address.",
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="User agent string.",
    )
    request_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="The URL path of the request.",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action was logged.",
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["model_name", "object_id"]),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.action} on {self.model_name} #{self.object_id} by {self.user or 'System'}"

    def get_changes_dict(self):
        """Return the changes field as a dict, or an empty dict if invalid."""
        try:
            return json.loads(self.changes) if self.changes else {}
        except json.JSONDecodeError:
            return {}

    @classmethod
    def log(
        cls,
        user,
        action,
        model,
        object_id,
        changes=None,
        ip_address=None,
        user_agent=None,
        request_path=None,
    ):
        """
        Convenience method to create an audit log entry.
        """
        try:
            changes_json = ""
            if changes:
                if isinstance(changes, dict):
                    changes_json = json.dumps(changes)
                else:
                    changes_json = str(changes)

            return cls.objects.create(
                user=user,
                action=action,
                model_name=model,
                object_id=str(object_id),
                changes=changes_json,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {e}")
            return None