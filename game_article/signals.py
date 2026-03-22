from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from main.i18n_backfill import (
    DEFAULT_BACKFILL_LANGS,
    TranslationBackfiller,
    backfill_instance_fields,
)

from .models import Article, ArticleCategory, ArticleTag


logger = logging.getLogger(__name__)
_BACKFILLER = None
_BACKFILLER_UNAVAILABLE = False

ARTICLE_CATEGORY_MAPPINGS = [
    ("name", "name_i18n", False),
    ("description", "description_i18n", False),
]
ARTICLE_TAG_MAPPINGS = [
    ("name", "name_i18n", False),
]
ARTICLE_MAPPINGS = [
    ("title", "title_i18n", False),
    ("author_name", "author_name_i18n", False),
    ("excerpt", "excerpt_i18n", False),
    ("summary", "summary_i18n", False),
    ("content", "content_i18n", True),
    ("read_time", "read_time_i18n", False),
]
PRIMARY_LOCALE = "zh-CN"


def _get_backfiller() -> TranslationBackfiller | None:
    global _BACKFILLER, _BACKFILLER_UNAVAILABLE
    if _BACKFILLER_UNAVAILABLE:
        return None
    if _BACKFILLER is None:
        try:
            _BACKFILLER = TranslationBackfiller()
        except Exception as exc:
            logger.warning("Auto i18n backfill disabled for game_article: %s", exc)
            _BACKFILLER_UNAVAILABLE = True
            return None
    return _BACKFILLER


def _sync_primary_locale_fields(instance, mappings, locale: str = PRIMARY_LOCALE) -> set[str]:
    changed_fields: set[str] = set()
    locale_key = str(locale or "").strip() or PRIMARY_LOCALE

    for mapping in mappings:
        source_field = str(mapping[0] if len(mapping) > 0 else "").strip()
        i18n_field = str(mapping[1] if len(mapping) > 1 else "").strip()
        if not source_field or not i18n_field:
            continue

        source_value = getattr(instance, source_field, "")
        source_text = "" if source_value is None else str(source_value)
        current_i18n = getattr(instance, i18n_field, {})
        payload = dict(current_i18n) if isinstance(current_i18n, dict) else {}

        if str(payload.get(locale_key, "")) == source_text:
            continue

        payload[locale_key] = source_text
        setattr(instance, i18n_field, payload)
        changed_fields.add(i18n_field)

    return changed_fields


def _auto_backfill(instance, mappings, raw: bool):
    if raw or not getattr(instance, "pk", None):
        return

    # Keep zh-CN as source-of-truth. When source fields change, refresh non-zh
    # i18n copies for the same field to avoid stale translated content/images.
    primary_changed_fields = set(_sync_primary_locale_fields(instance, mappings))
    changed_fields = set(primary_changed_fields)

    backfiller = _get_backfiller()
    if backfiller is not None:
        for mapping in mappings:
            i18n_field = str(mapping[1] if len(mapping) > 1 else "").strip()
            if not i18n_field:
                continue

            changed_fields.update(
                backfill_instance_fields(
                    instance,
                    [mapping],
                    DEFAULT_BACKFILL_LANGS,
                    overwrite=i18n_field in primary_changed_fields,
                    backfiller=backfiller,
                )
            )

    if not changed_fields:
        return

    update_kwargs = {field: getattr(instance, field) for field in changed_fields}
    instance.__class__.objects.filter(pk=instance.pk).update(**update_kwargs)


@receiver(post_save, sender=ArticleCategory)
def auto_backfill_article_category_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, ARTICLE_CATEGORY_MAPPINGS, raw)


@receiver(post_save, sender=ArticleTag)
def auto_backfill_article_tag_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, ARTICLE_TAG_MAPPINGS, raw)


@receiver(post_save, sender=Article)
def auto_backfill_article_i18n(sender, instance, raw=False, **kwargs):
    _auto_backfill(instance, ARTICLE_MAPPINGS, raw)
