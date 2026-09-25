from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Document(models.Model):
    class Category(models.TextChoices):
        FORM = 'FORM', 'Form'
        CIRCULAR = 'CIRCULAR', 'Circular'
        NOTIFICATION = 'NOTIFICATION', 'Notification'
        GUIDELINE = 'GUIDELINE', 'Guideline'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=200)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=14, choices=Category.choices, default=Category.OTHER)
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True)
    external_link = models.URLField(blank=True, help_text='Use this instead of a file for an external official link')
    description = models.TextField(blank=True)
    published = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.title

    @property
    def blurb(self):
        return self.description

    @property
    def url(self):
        if self.file:
            return self.file.url
        return self.external_link

    def clean(self):
        if not self.file and not self.external_link:
            raise ValidationError('Provide either a file or an external link.')
