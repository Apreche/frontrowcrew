from django.apps import AppConfig


class ShowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shows'

    def ready(self):
        # We're using decorators to connect the signals
        # But we need to import them
        from . import signals  # noqa
