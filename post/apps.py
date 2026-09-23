from django.apps import AppConfig


class PostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'post'

    def ready(self):
        # Import signals if audit is used
        try:
            import post.signals  # noqa
        except ImportError:
            pass