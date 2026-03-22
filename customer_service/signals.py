from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from main.i18n_backfill import (
    DEFAULT_BACKFILL_LANGS,
    TranslationBackfiller,
    backfill_instance_fields,
)

from .models import ContactMethod, CustomerServiceConfig, FAQ


logger = logging.getLogger(__name__)
_BACKFILLER = None
_BACKFILLER_UNAVAILABLE = False

CONTACT_METHOD_MAPPINGS = [
    ("title", "title_i18n", False),
    ("description", "description_i18n", False),
    ("button_text", "button_text_i18n", False),
]
FAQ_MAPPINGS = [
    ("question", "question_i18n", False),
    ("answer", "answer_i18n", False),
    ("category", "category_i18n", False),
]
CUSTOMER_SERVICE_CONFIG_MAPPINGS = [
    ("page_title", "page_title_i18n", False),
    ("page_description", "page_description_i18n", False),
    ("faq_title", "faq_title_i18n", False),
]


def _get_backfiller() -> TranslationBackfiller | None:
    global _BACKFILLER, _BACKFILLER_UNAVAILABLE
    if _BACKFILLER_UNAVAILABLE:
        return None
    if _BACKFILLER is None:
        try:
            _BACKFILLER = TranslationBackfiller()
        except Exception as exc:
            logger.warning("Auto i18n backfill disabled for customer_service: %s", exc)
            _BACKFILLER_UNAVAILABLE = True
            return None
    return _BACKFILLER


def _auto_backfill(instance, mappings, raw: bool):
    if raw or not getattr(instance, "pk", None):
        return

    backfiller = _get_backfiller()
    if backfiller is None:
        return

    changed_fields = backfill_instance_fields(
        instance,
        mappings,
        DEFAULT_BACKFILL_LANGS,
        overwrite=False,
        backfiller=backfiller,
    )
    if not changed_fields:
        return

    update_kwargs = {field: getattr(instance, field) for field in changed_fields}
    instance.__class__.objects.filter(pk=instance.pk).update(**update_kwargs)


@receiver(post_save, sender=ContactMethod)
def auto_backfill_contact_method_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, CONTACT_METHOD_MAPPINGS, raw)


@receiver(post_save, sender=FAQ)
def auto_backfill_faq_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, FAQ_MAPPINGS, raw)


@receiver(post_save, sender=CustomerServiceConfig)
def auto_backfill_customer_service_config_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, CUSTOMER_SERVICE_CONFIG_MAPPINGS, raw)
