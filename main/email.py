"""Custom Djoser email classes."""

from djoser import email as djoser_email
from django.conf import settings


class _FrontendOriginEmailMixin:
    def _inject_frontend_origin(self, context):
        context["protocol"] = getattr(settings, "FRONTEND_PROTOCOL", "") or "https"
        context["domain"] = (
            getattr(settings, "FRONTEND_DOMAIN", "")
            or settings.DJOSER.get("DOMAIN", "")
            or context.get("domain", "")
        )
        return context


class CustomActivationEmail(_FrontendOriginEmailMixin, djoser_email.ActivationEmail):
    """Activation email with environment-aware frontend domain/protocol."""

    def get_context_data(self):
        context = super().get_context_data()
        return self._inject_frontend_origin(context)


class CustomPasswordResetEmail(_FrontendOriginEmailMixin, djoser_email.PasswordResetEmail):
    """Password reset email with environment-aware frontend domain/protocol."""

    def get_context_data(self):
        context = super().get_context_data()
        return self._inject_frontend_origin(context)
