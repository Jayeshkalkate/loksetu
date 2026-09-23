from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'

    def ready(self):
        # Import signals if audit is installed
        try:
            import documents.signals  # noqa
        except ImportError:
            pass