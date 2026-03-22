from __future__ import annotations

import re
import time
from typing import Any, Iterable, Sequence

import requests
from bs4 import BeautifulSoup

from game_recharge.i18n_utils import normalize_locale_code


MAX_CHUNK_LEN = 4500
DEFAULT_BACKFILL_LANGS: tuple[str, ...] = (
    "en",
    "ja",
    "ko",
    "th",
    "vi",
    "zh-CN",
    "zh-TW",
    "fr",
    "de",
)


LOCALE_ALIASES = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "ja": "ja",
    "ja-jp": "ja",
    "ko": "ko",
    "ko-kr": "ko",
    "th": "th",
    "th-th": "th",
    "vi": "vi",
    "vi-vn": "vi",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-sg": "zh-CN",
    "zh-tw": "zh-TW",
    "zh-hk": "zh-TW",
    "zh-hant": "zh-TW",
    "fr": "fr",
    "fr-fr": "fr",
    "de": "de",
    "de-de": "de",
}


def parse_target_langs(raw_langs: Any) -> list[str]:
    if raw_langs is None:
        return list(DEFAULT_BACKFILL_LANGS)

    if isinstance(raw_langs, str):
        candidates = [item.strip() for item in raw_langs.split(",")]
    elif isinstance(raw_langs, Iterable):
        candidates = [str(item).strip() for item in raw_langs]
    else:
        candidates = [str(raw_langs).strip()]

    normalized: list[str] = []
    invalid: list[str] = []
    for item in candidates:
        if not item:
            continue
        alias_key = item.lower().replace("_", "-")
        locale = LOCALE_ALIASES.get(alias_key)
        if locale is None:
            invalid.append(item)
            continue
        canonical = normalize_locale_code(locale)
        if canonical not in normalized:
            normalized.append(canonical)

    if invalid:
        raise ValueError(f"Unsupported locale(s): {', '.join(invalid)}")
    if not normalized:
        return list(DEFAULT_BACKFILL_LANGS)
    return normalized


def _split_long_text(value: str) -> list[str]:
    text = str(value or "")
    if len(text) <= MAX_CHUNK_LEN:
        return [text]

    parts: list[str] = []
    current: list[str] = []
    current_len = 0

    for piece in re.split(r"(\n+)", text):
        piece_len = len(piece)
        if current and current_len + piece_len > MAX_CHUNK_LEN:
            parts.append("".join(current))
            current = []
            current_len = 0
        current.append(piece)
        current_len += piece_len

    if current:
        parts.append("".join(current))

    return parts or [text]


def _is_empty_translation_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    return False


def _is_translatable_json_text(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if re.match(r"^(https?:\/\/|\/|#)", text, flags=re.I):
        return False
    if re.match(r"^[\d\W_]+$", text, flags=re.U):
        return False
    return True


class TranslationBackfiller:
    def __init__(self) -> None:
        self._endpoint = "https://translate.googleapis.com/translate_a/single"
        self._session = requests.Session()
        self._session.headers.update(
            {"User-Agent": "Mozilla/5.0 (i18n-backfill-bot)"}
        )
        self._result_cache: dict[tuple[str, str], str] = {}

    def _translate_via_google(self, text: str, target_lang: str) -> str:
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }

        for attempt in range(2):
            try:
                response = self._session.get(self._endpoint, params=params, timeout=6)
                response.raise_for_status()
                data = response.json()
                if (
                    isinstance(data, list)
                    and data
                    and isinstance(data[0], list)
                ):
                    translated = "".join(
                        part[0]
                        for part in data[0]
                        if isinstance(part, list) and part and part[0] is not None
                    )
                    if translated:
                        return translated
            except Exception:
                if attempt < 1:
                    time.sleep(0.4)
                continue
        return text

    def translate_text(self, value: Any, target_lang: str) -> str:
        source_text = str(value or "")
        if not source_text.strip():
            return ""

        canonical_lang = normalize_locale_code(target_lang)
        if canonical_lang == "zh-CN":
            return source_text

        cache_key = (canonical_lang, source_text)
        cached = self._result_cache.get(cache_key)
        if cached is not None:
            return cached

        if len(source_text) <= MAX_CHUNK_LEN:
            translated = self._translate_via_google(source_text, canonical_lang)
        else:
            chunks = _split_long_text(source_text)
            translated = "".join(
                self._translate_via_google(chunk, canonical_lang) if chunk.strip() else chunk
                for chunk in chunks
            )

        final_text = str(translated or source_text)
        self._result_cache[cache_key] = final_text
        return final_text

    def translate_html(self, value: Any, target_lang: str) -> str:
        source_html = str(value or "")
        if not source_html.strip():
            return ""

        canonical_lang = normalize_locale_code(target_lang)
        if canonical_lang == "zh-CN":
            return source_html

        soup = BeautifulSoup(source_html, "html.parser")
        for text_node in soup.find_all(string=True):
            parent_name = (getattr(text_node.parent, "name", "") or "").lower()
            if parent_name in {"script", "style"}:
                continue

            original = str(text_node)
            stripped = original.strip()
            if not stripped:
                continue

            translated = self.translate_text(stripped, canonical_lang)
            if not translated:
                continue

            text_node.replace_with(original.replace(stripped, translated, 1))

        return str(soup)


def _translate_json_like(value: Any, target_lang: str, backfiller: TranslationBackfiller) -> Any:
    canonical_lang = normalize_locale_code(target_lang)
    if canonical_lang == "zh-CN":
        return value

    if isinstance(value, dict):
        return {
            key: _translate_json_like(item, canonical_lang, backfiller)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_translate_json_like(item, canonical_lang, backfiller) for item in value]
    if isinstance(value, tuple):
        return [_translate_json_like(item, canonical_lang, backfiller) for item in value]
    if isinstance(value, str):
        if not _is_translatable_json_text(value):
            return value
        translated = backfiller.translate_text(value, canonical_lang)
        return translated if str(translated or "").strip() else value
    return value


def backfill_instance_fields(
    instance: Any,
    mappings: Sequence[tuple[str, str, bool]],
    target_langs: Sequence[str] | None = None,
    *,
    overwrite: bool = False,
    backfiller: TranslationBackfiller | None = None,
) -> list[str]:
    langs = list(target_langs or DEFAULT_BACKFILL_LANGS)
    if not langs:
        langs = list(DEFAULT_BACKFILL_LANGS)

    translator = backfiller or TranslationBackfiller()
    changed_fields: list[str] = []

    for source_field, i18n_field, is_html in mappings:
        source_value = getattr(instance, source_field, "")
        is_structured_source = isinstance(source_value, (dict, list, tuple))
        source_text = str(source_value or "") if not is_structured_source else ""
        if is_structured_source and _is_empty_translation_value(source_value):
            continue
        if not is_structured_source and not source_text.strip():
            continue

        payload = getattr(instance, i18n_field, {}) or {}
        if not isinstance(payload, dict):
            payload = {}

        field_changed = False
        for lang in langs:
            canonical_lang = normalize_locale_code(lang)
            existing = payload.get(canonical_lang)
            if not overwrite and not _is_empty_translation_value(existing):
                continue

            if is_structured_source:
                translated = _translate_json_like(source_value, canonical_lang, translator)
                if _is_empty_translation_value(translated):
                    continue
            else:
                translated = (
                    translator.translate_html(source_text, canonical_lang)
                    if is_html
                    else translator.translate_text(source_text, canonical_lang)
                )
                if not str(translated or "").strip():
                    continue

            if payload.get(canonical_lang) != translated:
                payload[canonical_lang] = translated
                field_changed = True

        if field_changed:
            setattr(instance, i18n_field, payload)
            changed_fields.append(i18n_field)

    return changed_fields
