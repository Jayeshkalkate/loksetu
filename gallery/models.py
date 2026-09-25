from django.db import models


class GalleryImage(models.Model):
    class Category(models.TextChoices):
        EVENTS = 'EVENTS', 'Events'
        OFFICE = 'OFFICE', 'Office'
        CAMPAIGNS = 'CAMPAIGNS', 'Campaigns'
        AWARDS = 'AWARDS', 'Awards & Certificates'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.EVENTS)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded']

    def __str__(self):
        return self.title
