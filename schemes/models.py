from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid
from django.conf import settings
    
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

    # 🔹 Basic Info
    title = models.CharField(max_length=300, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)
    eligibility = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)

    # 🔹 Classification
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='General'
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='state'
    )

    # 🔹 Location Hierarchy
    state = models.CharField(max_length=100, default="Maharashtra")
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    # 🔹 External Link
    official_link = models.URLField(blank=True, null=True)

    # 🔹 Media
    image = models.ImageField(upload_to='schemes/', blank=True, null=True)

    # 🔹 Metadata
    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 FIXED: Properly inside class
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            # Ensure unique slug
            while Scheme.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            self.slug = slug

        super().save(*args, **kwargs)

    # 🔹 Admin friendly
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Scheme"
        verbose_name_plural = "Schemes"