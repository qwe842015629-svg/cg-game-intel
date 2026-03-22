from django.apps import AppConfig


class FooterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'footer'
    verbose_name = '页面底部管理'

    def ready(self):
        import footer.signals  # noqa: F401
