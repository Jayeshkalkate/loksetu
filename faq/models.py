from django.db import models


class FAQ(models.Model):
    category = models.CharField(max_length=100, default='General')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers show first within a category')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'order', 'id']

    def __str__(self):
        return self.question
