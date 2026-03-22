from django.apps import AppConfig


class GamePageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "game_page"
    verbose_name = "\u6e38\u620f\u9875\u9762\u7ba1\u7406"

    def ready(self):
        import game_page.signals  # noqa: F401
