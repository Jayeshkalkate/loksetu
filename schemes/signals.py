from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Scheme
from django.contrib.auth import get_user_model

from utils.email_service import send_new_scheme_email

User = get_user_model()


@receiver(post_save, sender=Scheme)
def scheme_created_email(sender, instance, created, **kwargs):

    if created:

        users = User.objects.exclude(email='')

        for user in users:
            send_new_scheme_email(
                user.email,
                instance
            )