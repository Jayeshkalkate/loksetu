import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


class Scheme(models.Model):
    LEVEL_CHOICES = [
        ('central', 'Central'),
        ('state', 'State'),
        ('district', 'District'),
        ('taluka', 'Taluka'),
        ('village', 'Village'),
    ]

    CATEGORY_CHOICES = [
        ('Education', 'Education'),
        ('Agriculture', 'Agriculture'),
        ('Health', 'Health'),
        ('Housing', 'Housing'),
        ('Employment', 'Employment'),
        ('Social Welfare', 'Social Welfare'),
        ('Women & Child Welfare', 'Women & Child Welfare'),
        ('Infrastructure', 'Infrastructure'),
        ('General', 'General'),
    ]

    # Basic Info
    title = models.CharField(max_length=300, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)
    eligibility = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)

    # Classification
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='state')

    # Location Hierarchy
    state = models.CharField(max_length=100, default="Maharashtra")
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    # External Link
    official_link = models.URLField(blank=True, null=True)

    # Media
    image = models.ImageField(upload_to='schemes/', blank=True, null=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_verified = models.BooleanField(default=False)  # Now default False to require approval
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['category']),
            models.Index(fields=['state']),
            models.Index(fields=['is_verified']),
        ]
        verbose_name = "Scheme"
        verbose_name_plural = "Schemes"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Scheme.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title