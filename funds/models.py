from django.db import models
from django.core.exceptions import ValidationError

# ==============================
# Location Model
# ==============================
class Location(models.Model):
    STATE = 'state'
    DISTRICT = 'district'
    TALUKA = 'taluka'
    VILLAGE = 'village'

    TYPE_CHOICES = [
        (STATE, 'State'),
        (DISTRICT, 'District'),
        (TALUKA, 'Taluka'),
        (VILLAGE, 'Village'),
    ]

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return f"{self.name} ({self.type})"


# ==============================
# Fund Model
# ==============================
class Fund(models.Model):
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=200)

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    released_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='funds')
    year = models.IntegerField()

    def clean(self):
        if self.released_amount > self.total_amount:
            raise ValidationError("Released > Total not allowed")

        if self.total_amount < 0 or self.released_amount < 0:
            raise ValidationError("Negative values not allowed")

    class Meta:
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['location']),
        ]

    @property
    def used_amount(self):
        return sum(p.used_amount for p in self.projects.all())

    @property
    def remaining_amount(self):
        return self.total_amount - self.used_amount

    def __str__(self):
        return f"{self.title} - {self.year}"

# ==============================
# Project Model
# ==============================
class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    name = models.CharField(max_length=255)

    sanctioned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    used_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🔥 Progress Calculation
    @property
    def progress_percentage(self):
        if self.sanctioned_amount == 0:
            return 0
        return round((self.used_amount / self.sanctioned_amount) * 100, 2)

    def __str__(self):
        return self.name


# ==============================
# Proof Model
# ==============================
class Proof(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='proofs'
    )

    image = models.ImageField(upload_to='proofs/')
    description = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.project.name}"


# ==============================
# Complaint Model
# ==============================
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='Complaints'
    )

    user_name = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint - {self.project.name} ({self.status})"
    
