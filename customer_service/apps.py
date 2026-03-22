from django.apps import AppConfig


class CustomerServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customer_service"
    verbose_name = "\u5ba2\u670d\u7ba1\u7406"

    def ready(self):
        import customer_service.signals  # noqa: F401
