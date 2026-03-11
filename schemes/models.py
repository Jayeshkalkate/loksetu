from django.db import models


SCHEME_LEVEL = (
    ('central', 'Central Scheme'),
    ('state', 'State Scheme'),
    ('district', 'District Scheme'),
    ('taluka', 'Taluka Scheme'),
    ('village', 'Village Scheme'),
)


class Scheme(models.Model):

    title = models.CharField(max_length=200)
    scheme_level = models.CharField(max_length=20, choices=SCHEME_LEVEL)

    source = models.CharField(max_length=200, blank=True, null=True)
    
    image = models.ImageField(upload_to="schemes/", blank=True, null=True)

    description = models.TextField()
    eligibility = models.TextField()
    benefits = models.TextField()

    state = models.CharField(max_length=100, default="Maharashtra")

    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    official_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)

    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title