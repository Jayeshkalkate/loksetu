from django.db import models


class Fund(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey('departments.Department', null=True, blank=True, on_delete=models.SET_NULL)
    financial_year = models.CharField(max_length=9, help_text='e.g. 2025-26')
    allocated_crore = models.DecimalField('Allocated (₹ crore)', max_digits=14, decimal_places=2)
    utilized_crore = models.DecimalField('Utilized (₹ crore)', max_digits=14, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    official_source = models.URLField(help_text='Official government page this information comes from')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-financial_year', 'name']

    def __str__(self):
        return f'{self.name} ({self.financial_year})'

    @property
    def blurb(self):
        return self.description

    @property
    def utilization_percent(self):
        if not self.allocated_crore:
            return 0
        return round(float(self.utilized_crore) / float(self.allocated_crore) * 100, 1)
