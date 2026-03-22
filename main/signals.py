import os
import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.i18n_backfill import (
    DEFAULT_BACKFILL_LANGS,
    TranslationBackfiller,
    backfill_instance_fields,
)

from .media_library import upsert_media_asset
from .models import Banner, HomeLayout

# Ignore these models to prevent recursion or duplicates
IGNORE_MODELS = ['MediaAsset', 'Session', 'LogEntry', 'ContentType', 'Permission', 'Group', 'User']

logger = logging.getLogger(__name__)
_BACKFILLER = None
_BACKFILLER_UNAVAILABLE = False

BANNER_I18N_MAPPINGS = [
    ("title", "title_i18n", False),
    ("description", "description_i18n", False),
    ("badge", "badge_i18n", False),
    ("primary_button_text", "primary_button_text_i18n", False),
    ("secondary_button_text", "secondary_button_text_i18n", False),
]

HOME_LAYOUT_I18N_MAPPINGS = [
    ("section_name", "section_name_i18n", False),
    ("config", "config_i18n", False),
]

@receiver(post_save)
def sync_images_to_media_library(sender, instance, created, **kwargs):
    """
    Signal to automatically sync any ImageField upload to the MediaAsset library.
    """
    # 1. Check if model should be ignored
    model_name = sender.__name__
    if model_name in IGNORE_MODELS:
        return

    # 2. Iterate over all fields to find ImageFields
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            file_field = getattr(instance, field.name)
            
            # Check if file exists and has content
            if file_field and hasattr(file_field, 'name') and file_field.name:
                filename = os.path.basename(file_field.name) or f"{model_name.lower()}-{field.name}.jpg"

                try:
                    upsert_media_asset(
                        file_obj=file_field,
                        requested_name=filename,
                        category='other',
                        alt_text=f"Synced from {model_name}",
                        create_thumbnail=True,
                    )
                except Exception as e:
                    print(f"Failed to sync image from {model_name} to MediaLibrary: {e}")


def _get_backfiller() -> TranslationBackfiller | None:
    global _BACKFILLER, _BACKFILLER_UNAVAILABLE
    if _BACKFILLER_UNAVAILABLE:
        return None
    if _BACKFILLER is None:
        try:
            _BACKFILLER = TranslationBackfiller()
        except Exception as exc:
            logger.warning("Auto i18n backfill disabled for main: %s", exc)
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


@receiver(post_save, sender=Banner)
def auto_backfill_banner_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, BANNER_I18N_MAPPINGS, raw)


@receiver(post_save, sender=HomeLayout)
def auto_backfill_home_layout_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, HOME_LAYOUT_I18N_MAPPINGS, raw)
