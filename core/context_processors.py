from django.conf import settings


def site(request):
    return {'CONTACT_EMAIL': settings.CONTACT_EMAIL,
            'SOCIAL_LINKS': {k: v for k, v in settings.SOCIAL_LINKS.items() if v}}
