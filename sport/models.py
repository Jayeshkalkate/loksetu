from django.db import models

class Tournament(models.Model):

    title = models.CharField(max_length=200)
    village = models.CharField(max_length=200)
    district = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    cricheroes_link = models.URLField()

    poster = models.ImageField(upload_to='tournaments/', blank=True, null=True)

    is_verified = models.BooleanField(default=False)   # ⭐ NEW FIELD

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title