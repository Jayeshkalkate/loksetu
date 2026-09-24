from django.db import models


class EmergencyContact(models.Model):
    category = models.CharField(max_length=80)
    name = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)
    official_source = models.URLField(blank=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} ({self.category})'

    @property
    def blurb(self):
        return self.description
