from django.apps import AppConfig


class OpsGatewayConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ops_gateway"
    verbose_name = "Ops Gateway"

    def ready(self):
        try:
            from .auto_runner import start_auto_runner

            start_auto_runner()
        except Exception:
            # Keep app startup resilient even if scheduler bootstrap fails.
            pass
