from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        ONGOING = 'ONGOING', 'Ongoing'
        COMPLETED = 'COMPLETED', 'Completed'
        DELAYED = 'DELAYED', 'Delayed'

    name = models.CharField(max_length=200)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey('departments.District', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)
    description = models.TextField()
    budget_crore = models.DecimalField('Budget (₹ crore)', max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    official_source = models.URLField(help_text='Official government page this information comes from')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.name

    @property
    def blurb(self):
        return self.description

    @property
    def status_color(self):
        return {'PLANNED': 'secondary', 'ONGOING': 'primary',
                'COMPLETED': 'success', 'DELAYED': 'danger'}.get(self.status, 'secondary')
