from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Report(models.Model):
    class ReportType(models.TextChoices):
        ANNUAL = 'ANNUAL', 'Annual report'
        PERFORMANCE = 'PERFORMANCE', 'Performance report'
        AUDIT = 'AUDIT', 'Audit report'
        SURVEY = 'SURVEY', 'Survey / study'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=200)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    report_type = models.CharField(max_length=12, choices=ReportType.choices, default=ReportType.OTHER)
    summary = models.TextField()
    file = models.FileField(upload_to='reports/%Y/%m/', blank=True)
    external_link = models.URLField(blank=True, help_text='Use this instead of a file for an external official link')
    official_source = models.URLField(blank=True)
    published = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.title

    @property
    def blurb(self):
        return self.summary

    @property
    def url(self):
        if self.file:
            return self.file.url
        return self.external_link

    def clean(self):
        if not self.file and not self.external_link:
            raise ValidationError('Provide either a file or an external link.')
