from django.db import models


class Department(models.Model):
    CATEGORY_CHOICES = [
        ('ADMIN', 'Administration & Governance'),
        ('AGRI', 'Agriculture & Rural Development'),
        ('HEALTH', 'Health & Family Welfare'),
        ('EDU', 'Education & Skills'),
        ('LABOUR', 'Employment & Labour'),
        ('INDUSTRY', 'Industry & Economy'),
        ('URBAN', 'Housing & Urban Development'),
        ('ENV', 'Environment & Natural Resources'),
        ('SAFETY', 'Public Safety & Justice'),
        ('TRANSPORT', 'Transport'),
        ('WELFARE', 'Social Welfare'),
        ('CULTURE', 'Culture & Tourism'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='OTHER')
    description = models.TextField(blank=True, help_text='What this department does, in plain language')
    responsibilities = models.TextField(blank=True, help_text='One responsibility per line')

    # Contact directory
    hod_name = models.CharField('Head of Department', max_length=150, blank=True)
    hod_designation = models.CharField(max_length=150, blank=True)
    phone = models.CharField('Office phone', max_length=40, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    website = models.URLField('Official website', blank=True)

    # Citizen help
    citizen_helpline = models.CharField(max_length=40, blank=True)
    grievance_officer = models.CharField(max_length=150, blank=True)
    grievance_portal_url = models.URLField(blank=True)
    rti_officer = models.CharField('Public Information Officer (RTI)', max_length=150, blank=True)
    rti_appellate_authority = models.CharField(max_length=150, blank=True)

    # Trust / sourcing
    source_url = models.URLField(blank=True, help_text='Official government page this profile is based on')
    last_verified = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def blurb(self):
        return self.description

    @property
    def responsibilities_list(self):
        return [line.strip() for line in self.responsibilities.splitlines() if line.strip()]

    @property
    def scheme_count(self):
        return self.scheme_set.count()

    @property
    def officer_count(self):
        return self.officers.count()


class DepartmentOfficer(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='officers')
    name = models.CharField(max_length=150, blank=True, help_text='Leave blank to show only the designation')
    designation = models.CharField(max_length=150)
    responsibility = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name or self.designation} ({self.department})'


class District(models.Model):
    name = models.CharField(max_length=80, unique=True)
    division = models.CharField(max_length=80, blank=True, help_text='Revenue division, e.g. Nashik Division')
    headquarters = models.CharField(max_length=80, blank=True)
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    population = models.PositiveIntegerField(null=True, blank=True)
    population_reference_year = models.PositiveSmallIntegerField(null=True, blank=True)
    talukas = models.PositiveIntegerField(null=True, blank=True)
    villages = models.PositiveIntegerField(null=True, blank=True)
    overview = models.TextField(blank=True)
    source_url = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
