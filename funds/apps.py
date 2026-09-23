from django.apps import AppConfig


class FundsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funds'

    def ready(self):
        try:
            import funds.signals  # noqa
        except ImportError:
            pass