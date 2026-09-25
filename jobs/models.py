from django.db import models


class JobNotification(models.Model):
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    description = models.TextField()
    eligibility = models.TextField(blank=True)
    last_date = models.DateField(help_text='Last date to apply', null=True, blank=True)
    application_link = models.URLField(blank=True)
    official_source = models.URLField(blank=True, help_text='Official notification / government source')
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return f'{self.title} — {self.organization}'

    @property
    def blurb(self):
        return f'{self.organization}\n\n{self.description}'
