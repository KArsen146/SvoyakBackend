from django.apps import AppConfig


class PacksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.packs'

    def ready(self):
        import core.packs.receivers