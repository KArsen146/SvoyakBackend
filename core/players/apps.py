from django.apps import AppConfig


class PlayersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.players'

    def ready(self):
        import core.players.receivers
