from __future__ import annotations

from typing import Any


SUPPORTED_LOCALES = ("zh-CN", "zh-TW", "en", "ja", "ko", "fr", "de", "vi", "th")
DEFAULT_LOCALE = "zh-CN"


def normalize_locale_code(raw_locale: Any) -> str:
    value = str(raw_locale or "").strip().lower()
    if not value:
        return DEFAULT_LOCALE

    if value.startswith("zh"):
        if any(tag in value for tag in ("tw", "hk", "hant")):
            return "zh-TW"
        return "zh-CN"
    if value.startswith("en"):
        return "en"
    if value.startswith("ja"):
        return "ja"
    if value.startswith("ko"):
        return "ko"
    if value.startswith("fr"):
        return "fr"
    if value.startswith("de"):
        return "de"
    if value.startswith("vi"):
        return "vi"
    if value.startswith("th"):
        return "th"
    return DEFAULT_LOCALE


def _header_accept_language(request) -> str:
    if request is None:
        return ""
    return str(request.META.get("HTTP_ACCEPT_LANGUAGE") or "").strip()


def resolve_request_locale(request, default: str = DEFAULT_LOCALE) -> str:
    if request is None:
        return normalize_locale_code(default)

    query_locale = ""
    try:
        query_locale = str(request.query_params.get("locale") or "").strip()
    except Exception:
        query_locale = str(getattr(request, "GET", {}).get("locale") or "").strip()
    if query_locale:
        return normalize_locale_code(query_locale)

    header_locale = str(request.META.get("HTTP_X_LOCALE") or "").strip()
    if header_locale:
        return normalize_locale_code(header_locale)

    accept_language = _header_accept_language(request)
    if accept_language:
        primary = accept_language.split(",", 1)[0].split(";", 1)[0].strip()
        if primary:
            return normalize_locale_code(primary)

    return normalize_locale_code(default)


def _locale_aliases(locale: str) -> list[str]:
    normalized = normalize_locale_code(locale)
    aliases = [normalized, normalized.lower(), normalized.replace("-", "_"), normalized.lower().replace("-", "_")]

    if normalized == "zh-CN":
        aliases.extend(["zh", "zh-cn", "zh_cn", "zh-hans", "zh_hans"])
    elif normalized == "zh-TW":
        aliases.extend(["zh", "zh-tw", "zh_tw", "zh-hk", "zh_hk", "zh-hant", "zh_hant"])
    elif normalized == "en":
        aliases.extend(["en-us", "en_us", "en-gb", "en_gb"])

    base = normalized.split("-", 1)[0].lower()
    aliases.append(base)
    deduped = []
    for alias in aliases:
        item = str(alias or "").strip()
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _pick_from_dict(i18n_map: dict[str, Any], locale: str) -> str:
    if not isinstance(i18n_map, dict):
        return ""
    if not i18n_map:
        return ""

    alias_chain = _locale_aliases(locale)
    normalized_pairs = []
    for key, value in i18n_map.items():
        key_text = str(key or "").strip()
        if not key_text:
            continue
        normalized_pairs.append((key_text, value))
        normalized_pairs.append((key_text.lower(), value))
        normalized_pairs.append((key_text.replace("_", "-").lower(), value))

    # Prefer requested locale.
    for alias in alias_chain:
        for key, value in normalized_pairs:
            if key == alias:
                text = str(value or "").strip()
                if text:
                    return text

    # Fallback chain: English -> Simplified Chinese.
    for fallback_locale in ("en", "zh-CN"):
        for alias in _locale_aliases(fallback_locale):
            for key, value in normalized_pairs:
                if key == alias:
                    text = str(value or "").strip()
                    if text:
                        return text

    return ""


def localize_text(default_text: Any, i18n_map: Any, locale: str) -> str:
    translated = _pick_from_dict(i18n_map if isinstance(i18n_map, dict) else {}, locale)
    if translated:
        return translated
    return str(default_text or "").strip()


def localize_text_with_variants(locale: str, *variants: tuple[Any, Any]) -> str:
    """
    Choose localized text from (default_text, i18n_map) variants in order.

    Example:
      localize_text_with_variants(locale, (title, title_i18n), (title_tw, {}))
    """
    for default_text, i18n_map in variants:
        value = localize_text(default_text, i18n_map, locale)
        if value:
            return value
    return ""
