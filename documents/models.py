import os
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify

User = get_user_model()


def document_upload_path(instance, filename):
    """
    Generate a unique file path: documents/user_<id>/<uuid>_<original_filename>
    """
    ext = filename.split('.')[-1] if '.' in filename else ''
    # Sanitize filename
    base_name = slugify(os.path.splitext(filename)[0][:50])
    unique_name = f"{uuid.uuid4().hex[:8]}_{base_name}"
    if ext:
        unique_name += f".{ext}"
    return f"documents/user_{instance.uploaded_by.id}/{unique_name}"


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'txt'])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False, help_text="If checked, any authenticated user can view/download.")

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_by', 'uploaded_at']),
            models.Index(fields=['is_public']),
        ]
        permissions = [
            ("can_delete_any_document", "Can delete any document"),
        ]

    def __str__(self):
        return self.title

    def get_file_size(self):
        """Return file size in human-readable format."""
        if self.file and hasattr(self.file, 'size'):
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "Unknown"

    def extension(self):
        return os.path.splitext(self.file.name)[1][1:] if self.file else ''