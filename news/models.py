from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    source_url = models.URLField(blank=True)
    is_official = models.BooleanField(default=False, help_text='Tick only if taken from an authoritative government source')
    published = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.title

    @property
    def blurb(self):
        return self.body
