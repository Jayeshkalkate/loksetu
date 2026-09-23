from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    CATEGORY_CHOICES = [
        ("announcement", "Announcement"),
        ("update", "Update"),
        ("alert", "Alert"),
        ("scheme", "Scheme"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='posts/')
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="announcement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
            models.Index(fields=['category']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title