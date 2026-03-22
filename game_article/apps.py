from django.apps import AppConfig


class GameArticleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game_article'

    def ready(self):
        import game_article.signals  # noqa: F401
