from django.db import models


class Scheme(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    eligibility = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    documents_required = models.TextField(blank=True)
    application_process = models.TextField(blank=True)
    application_link = models.URLField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    official_source = models.URLField(help_text='Official government page this information comes from')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def blurb(self):
        return self.description
