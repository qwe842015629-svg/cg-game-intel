import json
import logging
import re
import time
from html import escape
from pathlib import Path
from typing import Any

import requests
from decouple import config

logger = logging.getLogger(__name__)

DEFAULT_POLO_BASE_URL = "https://work.poloapi.com"
DEFAULT_POLO_MODEL = "grok-4-fast"
DEFAULT_OPENAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_OPENAI_MODEL = "grok-4-fast"

_BANNED_WORD_REPLACEMENTS = (
    ("全方位", "完整"),
    ("解析", "說明"),
    ("全面", "完整"),
    ("指南", "攻略"),
    ("高效", "快速"),
)

_FORUM_NOISE_PATTERNS = (
    r"(?i)\b(?:gp|bp)\b",
    r"[@＠][\w\u4e00-\u9fff]{2,20}",
    r"(?:留言|回覆|回复|樓主|楼主|網友|网友|推|噓|→)",
    r"(?:巴幣|巴币|姆咪|卡位|沙發|沙发|簽到|签到)",
    r"(?:https?://\S+)",
)

_QUALITY_MIN_TEXT_LEN = 900
_QUALITY_MIN_H2 = 3
_QUALITY_MIN_H3 = 2

_GARBLED_QMARK_PATTERN = re.compile(r"\?{3,}")
_GARBLED_REPLACEMENT_CHAR = "\uFFFD"


def rewrite_bahamut_text(
    raw_text: str,
    game_name: str,
    keywords: list[str] | None = None,
) -> dict[str, Any]:
    """
    Convert raw forum text into SEO article JSON.

    Returned JSON keys:
    - title
    - body_html
    - tags
    - meta_description
    - meta_title
    - diagnostics
    """
    normalized_lines = _extract_meaningful_lines(raw_text)
    merged_text = "\n".join(normalized_lines)
    tag_list = _build_tags(game_name, keywords)
    llm_cfg = _resolve_llm_config()

    source_text = merged_text or raw_text

    if llm_cfg["api_key"]:
        llm_result, llm_error = _rewrite_with_llm(
            llm_cfg=llm_cfg,
            raw_text=source_text,
            game_name=game_name,
            tags=tag_list,
        )
        if llm_result:
            return _postprocess_rewrite_result(
                result=llm_result,
                llm_cfg=llm_cfg,
                source_text=source_text,
                game_name=game_name,
                tags=tag_list,
            )
        fallback_reason = llm_error or "llm_failed"
    else:
        fallback_reason = "missing_api_key"

    fallback_result = _build_fallback_result(
        raw_text=source_text,
        game_name=game_name,
        tags=tag_list,
        fallback_reason=fallback_reason,
    )
    return _postprocess_rewrite_result(
        result=fallback_result,
        llm_cfg=llm_cfg,
        source_text=source_text,
        game_name=game_name,
        tags=tag_list,
    )


def test_llm_connection(
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout_seconds: int = 45,
) -> dict[str, Any]:
    """
    Lightweight connectivity test for configured LLM endpoint.

    Returns a JSON-safe dict with:
    - success: bool
    - message: str
    - endpoint/style/model/http_status/latency_ms
    - preview (on success) or error (on failure)
    """
    normalized_base_url = str(base_url or "").strip().rstrip("/")
    normalized_api_key = str(api_key or "").strip()
    normalized_model = str(model or "").strip() or DEFAULT_OPENAI_MODEL
    normalized_timeout = _coerce_positive_int(timeout_seconds, default=45)

    if not normalized_base_url:
        return {
            "success": False,
            "message": "missing_base_url",
            "error": "Base URL is required",
        }
    if not normalized_api_key:
        return {
            "success": False,
            "message": "missing_api_key",
            "error": "API Key is required",
        }

    style = _detect_api_style(
        provider_hint="auto",
        base_url=normalized_base_url,
        model=normalized_model,
    )
    endpoint = (
        _build_gemini_generate_content_url(base_url=normalized_base_url, model=normalized_model)
        if style == "gemini_generate_content"
        else _build_openai_chat_url(base_url=normalized_base_url)
    )

    started_at = time.perf_counter()
    try:
        if style == "gemini_generate_content":
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": 'Reply exactly with: {"ok": true}'}],
                    }
                ]
            }
            response = _post_with_auth_variants(
                url=endpoint,
                payload=payload,
                api_key=normalized_api_key,
                timeout_seconds=normalized_timeout,
                prefer_bearer=False,
            )
            response.raise_for_status()
            response_data = response.json()
            content_preview = _extract_gemini_text(response_data)
        else:
            payload = {
                "model": normalized_model,
                "temperature": 0,
                "max_tokens": 16,
                "messages": [
                    {"role": "system", "content": "You are a health check endpoint."},
                    {"role": "user", "content": 'Reply exactly with: {"ok": true}'},
                ],
            }
            response = _post_with_auth_variants(
                url=endpoint,
                payload=payload,
                api_key=normalized_api_key,
                timeout_seconds=normalized_timeout,
                prefer_bearer=True,
            )
            response.raise_for_status()
            response_data = response.json()
            content_preview = _extract_openai_content(response_data)

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        return {
            "success": True,
            "message": "connection_ok",
            "style": style,
            "endpoint": endpoint,
            "model": normalized_model,
            "http_status": response.status_code,
            "latency_ms": elapsed_ms,
            "preview": str(content_preview or "").strip()[:120],
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        return {
            "success": False,
            "message": "connection_failed",
            "style": style,
            "endpoint": endpoint,
            "model": normalized_model,
            "latency_ms": elapsed_ms,
            "error": _format_llm_error(exc),
        }


def _resolve_llm_config() -> dict[str, Any]:
    db_cfg = _load_db_llm_config()
    env_api_key = _first_non_empty(
        config("POLO_API_KEY", default=""),
        config("BAHAMUT_API_KEY", default=""),
        config("LLM_API_KEY", default=""),
        config("OPENAI_API_KEY", default=""),
    )
    env_base_url = _first_non_empty(
        config("XAI_BASE_URL", default=""),
        config("POLO_API_BASE_URL", default=""),
        config("BAHAMUT_API_BASE_URL", default=""),
        config("LLM_API_BASE_URL", default=""),
        config("OPENAI_API_BASE_URL", default=""),
        config("OPENAI_API_BASE", default=""),
        DEFAULT_OPENAI_BASE_URL,
    )
    env_model = _first_non_empty(
        config("XAI_MODEL", default=""),
        config("POLO_API_MODEL", default=""),
        config("BAHAMUT_API_MODEL", default=""),
        config("LLM_MODEL", default=""),
        config("OPENAI_MODEL", default=""),
        DEFAULT_OPENAI_MODEL,
    )
    cfg_file = _load_google_api_config()

    db_api_key = str(db_cfg.get("api_key") or "").strip()
    use_db_override = bool(db_api_key)

    if use_db_override:
        api_key = _first_non_empty(
            db_api_key,
            env_api_key,
            str(cfg_file.get("api_key") or ""),
        )
        base_url = _first_non_empty(
            str(db_cfg.get("base_url") or ""),
            env_base_url,
            str(cfg_file.get("base_url") or ""),
            DEFAULT_OPENAI_BASE_URL,
        )
        model = _first_non_empty(
            str(db_cfg.get("model_name") or ""),
            env_model,
            str(cfg_file.get("model") or ""),
            DEFAULT_OPENAI_MODEL,
        )
        provider_hint = _first_non_empty(
            str(db_cfg.get("provider_hint") or ""),
            config("LLM_PROVIDER", default="auto").strip().lower(),
        )
        timeout_seconds = _coerce_positive_int(
            db_cfg.get("timeout_seconds"),
            default=config("LLM_TIMEOUT_SECONDS", default=45, cast=int),
        )
    else:
        api_key = _first_non_empty(
            env_api_key,
            str(cfg_file.get("api_key") or ""),
        )
        base_url = _first_non_empty(
            env_base_url,
            str(cfg_file.get("base_url") or ""),
            DEFAULT_OPENAI_BASE_URL,
        )
        model = _first_non_empty(
            env_model,
            str(cfg_file.get("model") or ""),
            DEFAULT_OPENAI_MODEL,
        )
        provider_hint = config("LLM_PROVIDER", default="auto").strip().lower()
        timeout_seconds = config("LLM_TIMEOUT_SECONDS", default=45, cast=int)

    style = _detect_api_style(
        provider_hint=provider_hint,
        base_url=base_url,
        model=model,
    )
    return {
        "api_key": api_key.strip(),
        "base_url": base_url.strip().rstrip("/"),
        "model": model.strip(),
        "style": style,
        "timeout_seconds": timeout_seconds,
    }


def _load_db_llm_config() -> dict[str, Any]:
    try:
        from seo_automation.models import LLMApiSetting

        setting = LLMApiSetting.objects.filter(is_active=True).order_by("-updated_at", "-id").first()
        if not setting:
            return {}
        return {
            "base_url": setting.base_url,
            "api_key": setting.api_key,
            "model_name": setting.model_name,
            "timeout_seconds": setting.timeout_seconds,
        }
    except Exception:
        return {}


def _detect_api_style(*, provider_hint: str, base_url: str, model: str) -> str:
    if provider_hint in {"polo", "bahamut", "gemini"}:
        return "gemini_generate_content"
    if provider_hint in {"openai", "openai_compat", "chat_completions", "xai", "grok"}:
        return "openai_chat_completions"

    lowered_url = base_url.lower()
    lowered_model = model.lower()
    # Apifox doc for work.poloapi.com uses OpenAI-compatible chat endpoint.
    if "work.poloapi.com" in lowered_url:
        return "openai_chat_completions"
    if "/v1beta/models" in lowered_url:
        return "gemini_generate_content"
    if lowered_model.startswith("gemini"):
        return "gemini_generate_content"
    if lowered_model.startswith("grok"):
        return "openai_chat_completions"
    return "openai_chat_completions"


def _rewrite_with_llm(
    *,
    llm_cfg: dict[str, Any],
    raw_text: str,
    game_name: str,
    tags: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    if llm_cfg["style"] == "gemini_generate_content":
        return _rewrite_with_gemini_generate_content(
            api_key=llm_cfg["api_key"],
            base_url=llm_cfg["base_url"] or DEFAULT_POLO_BASE_URL,
            model=llm_cfg["model"] or DEFAULT_POLO_MODEL,
            timeout_seconds=llm_cfg["timeout_seconds"],
            raw_text=raw_text,
            game_name=game_name,
            tags=tags,
        )

    return _rewrite_with_openai_chat_completions(
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg["base_url"] or DEFAULT_OPENAI_BASE_URL,
        model=llm_cfg["model"] or DEFAULT_OPENAI_MODEL,
        timeout_seconds=llm_cfg["timeout_seconds"],
        raw_text=raw_text,
        game_name=game_name,
        tags=tags,
    )


def _rewrite_with_gemini_generate_content(
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout_seconds: int,
    raw_text: str,
    game_name: str,
    tags: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    prompt = _build_prompt_for_rewrite(game_name=game_name, tags=tags, raw_text=raw_text)
    url = _build_gemini_generate_content_url(base_url=base_url, model=model)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    try:
        response = _post_with_auth_variants(
            url=url,
            payload=payload,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            prefer_bearer=False,
        )
        response.raise_for_status()
        response_data = response.json()
        model_text = _extract_gemini_text(response_data)
        parsed = _extract_json_object(model_text)
        normalized = _normalize_llm_result(parsed, game_name, tags)
        normalized["diagnostics"] = {
            "provider": "polo_gemini_compatible",
            "model": model,
            "endpoint": url,
            "fallback": False,
        }
        return normalized, None
    except Exception as exc:
        error_text = _format_llm_error(exc)
        logger.warning("Gemini-compatible rewrite failed, fallback mode. reason=%s", error_text)
        return None, error_text


def _rewrite_with_openai_chat_completions(
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout_seconds: int,
    raw_text: str,
    game_name: str,
    tags: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    system_prompt = (
        "你是資深遊戲媒體編輯與 SEO 策略師，熟悉巴哈姆特討論區文風與台灣繁體中文語感。"
        "你必須輸出嚴格 JSON 物件，不要輸出程式碼區塊，不要輸出解釋。"
    )
    user_prompt = _build_prompt_for_rewrite(game_name=game_name, tags=tags, raw_text=raw_text)
    payload = {
        "model": model,
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    url = _build_openai_chat_url(base_url=base_url)

    try:
        response = _post_with_auth_variants(
            url=url,
            payload=payload,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            prefer_bearer=True,
        )
        response.raise_for_status()
        response_data = response.json()
        content = _extract_openai_content(response_data)
        parsed = _extract_json_object(content)
        normalized = _normalize_llm_result(parsed, game_name, tags)
        normalized["diagnostics"] = {
            "provider": "openai_compatible",
            "model": model,
            "endpoint": url,
            "fallback": False,
        }
        return normalized, None
    except Exception as exc:
        error_text = _format_llm_error(exc)
        logger.warning("OpenAI-compatible rewrite failed, fallback mode. reason=%s", error_text)
        return None, error_text

def _post_with_auth_variants(
    *,
    url: str,
    payload: dict[str, Any],
    api_key: str,
    timeout_seconds: int,
    prefer_bearer: bool,
) -> requests.Response:
    auth_values = [api_key, f"Bearer {api_key}"]
    if prefer_bearer:
        auth_values = [f"Bearer {api_key}", api_key]

    last_response: requests.Response | None = None
    last_error: Exception | None = None
    for auth_value in auth_values:
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": auth_value,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=(15, timeout_seconds),
            )
            last_response = response
            if response.status_code in (401, 403):
                continue
            return response
        except Exception as exc:
            last_error = exc
            continue

    if last_response is not None:
        return last_response
    raise RuntimeError(f"LLM request failed before response: {last_error}")


def _build_prompt_for_rewrite(*, game_name: str, tags: list[str], raw_text: str) -> str:
    preferred_keywords = "、".join(tags[:12]) or game_name
    return (
        "你要把論壇內容改寫成可直接發布的【攻略文章】。\n"
        "必須嚴格遵守以下規則：\n"
        "1) 標題與正文都使用台灣繁體中文，語氣口語、像玩家分享，不要新聞腔與 AI 腔。\n"
        "2) 採用 Google headers 結構：1 個 <h1>、至少 3 個 <h2>、至少 2 個 <h3>，並使用 <p>/<ul>/<li>/<strong>。\n"
        "3) body_html 只能是 HTML 片段，不得包含 <html>/<head>/<body>/<style>/<script>。\n"
        "4) 開頭先寫 1 段導語（120-220 字）說明這篇會幫玩家解決什麼問題。\n"
        "5) 文章長度目標約 1000 字，內容不要壓縮，請把每個重點展開成段落。\n"
        "6) 內容要包含可執行資訊：版本重點、實戰技巧、儲值/充值流程、安全提醒、常見問題。\n"
        "7) 儲值/充值段落需自然提到可在本站同款遊戲頁完成操作與查單，語氣像玩家建議，不要廣告口吻。\n"
        "8) 結尾加入 1 個精簡重點表格（2 欄即可）。\n"
        "9) 適度加入表情符號（例如 ✨、🎯、🧭、🛡️），但不要過量；條列重點請優先使用 emoji 作為項目符號。\n"
        "10) 若引用到有價值連結，請保留並使用 <a href=\"...\">...</a>；移除無關或垃圾連結。\n"
        "11) 嚴禁在標題/小標/內文出現：全方位、解析、全面、指南、高效。\n"
        "12) 先在內部產生 3-5 個不重複候選標題並自行篩選最佳標題；最終只輸出 1 篇最佳版本，不要輸出候選清單。\n"
        "13) 真人撰寫感至少 80%，避免模板化句型。\n"
        "14) 僅可基於來源內容改寫，不可捏造事實，資訊真實度目標 98%-100%。\n"
        "15) meta_title <= 60 字；meta_description <= 160 字。\n"
        "16) 僅輸出 JSON 物件，鍵名必須且只能包含：\n"
        "    title, body_html, tags, meta_description, meta_title\n\n"
        f"遊戲名稱：{game_name}\n"
        f"優先關鍵詞：{preferred_keywords}\n"
        "來源原文：\n"
        f"{raw_text}"
    )

def _build_gemini_generate_content_url(*, base_url: str, model: str) -> str:
    value = (base_url or DEFAULT_POLO_BASE_URL).strip().rstrip("/")
    if ":generateContent" in value:
        return value
    if value.endswith("/v1beta/models"):
        return f"{value}/{model}:generateContent"
    if "/v1beta/models/" in value:
        return f"{value}:generateContent"
    return f"{value}/v1beta/models/{model}:generateContent"


def _build_openai_chat_url(*, base_url: str) -> str:
    value = (base_url or DEFAULT_OPENAI_BASE_URL).strip().rstrip("/")
    if value.endswith("/chat/completions"):
        return value
    if value.endswith("/v1"):
        return f"{value}/chat/completions"
    return f"{value}/v1/chat/completions"


def _extract_gemini_text(response_data: dict[str, Any]) -> str:
    candidates = response_data.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini response has no candidates")
    first = candidates[0] or {}
    content = first.get("content") or {}
    parts = content.get("parts") or []
    if not parts:
        raise ValueError("Gemini response has no parts")
    text = parts[0].get("text")
    if not text:
        raise ValueError("Gemini response text is empty")
    return str(text)


def _extract_openai_content(response_data: dict[str, Any]) -> str:
    choices = response_data.get("choices") or []
    if not choices:
        raise ValueError("OpenAI response has no choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(str(part["text"]))
            elif isinstance(part, str):
                text_parts.append(part)
        joined = "".join(text_parts).strip()
        if joined:
            return joined
    raise ValueError("OpenAI message content is empty")


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("LLM output is not a valid JSON object")


def _normalize_llm_result(
    parsed: dict[str, Any],
    game_name: str,
    tags: list[str],
) -> dict[str, Any]:
    title = _apply_text_guardrails(str(parsed.get("title") or "").strip())
    body_html = str(parsed.get("body_html") or "").strip()
    meta_description = _apply_text_guardrails(str(parsed.get("meta_description") or "").strip())
    meta_title = _apply_text_guardrails(str(parsed.get("meta_title") or "").strip())
    llm_tags = parsed.get("tags") or []

    fallback_title = _apply_text_guardrails(f"{game_name} 儲值與版本重點懶人包")
    title = _repair_garbled_text(
        title,
        game_name=game_name,
        fallback=fallback_title,
    )
    if not body_html:
        body_html = _build_basic_html(game_name, [])
    elif not _contains_html_tag(body_html):
        body_html = _coerce_plain_text_to_html(body_html, game_name)
    body_html = _repair_garbled_html(body_html, game_name=game_name)
    body_html = _apply_html_guardrails(body_html)
    fallback_meta_description = _apply_text_guardrails(
        f"{game_name} 版本重點、實戰技巧、儲值流程與帳號安全重點一次整理。"
    )
    meta_description = _repair_garbled_text(
        meta_description,
        game_name=game_name,
        fallback=fallback_meta_description,
    )
    meta_title = _repair_garbled_text(
        meta_title,
        game_name=game_name,
        fallback=title[:60],
    )
    meta_title = _apply_text_guardrails(meta_title)

    if not isinstance(llm_tags, list):
        llm_tags = []

    merged_tags = _dedupe_tags([*llm_tags, *tags])[:10]
    cleaned_tags = _dedupe_tags([_apply_text_guardrails(tag) for tag in merged_tags])[:10]
    return {
        "title": title[:220],
        "body_html": body_html,
        "tags": cleaned_tags,
        "meta_description": meta_description[:160],
        "meta_title": meta_title[:60],
    }

def _build_fallback_result(
    *,
    raw_text: str,
    game_name: str,
    tags: list[str],
    fallback_reason: str,
) -> dict[str, Any]:
    lines = _extract_meaningful_lines(raw_text)
    title = _apply_text_guardrails(f"{game_name} 版本重點與代儲流程整理")
    body_html = _apply_html_guardrails(_build_basic_html(game_name, lines))
    meta_description = _apply_text_guardrails(
        f"{game_name} 版本重點、玩法建議、代儲流程與安全提醒，重點一次看懂。"
    )[:160]

    return {
        "title": title,
        "body_html": body_html,
        "tags": _dedupe_tags([_apply_text_guardrails(tag) for tag in tags])[:10],
        "meta_description": meta_description,
        "meta_title": title[:60],
        "diagnostics": {
            "provider": "fallback",
            "model": "",
            "fallback": True,
            "reason": fallback_reason,
        },
    }


def _postprocess_rewrite_result(
    *,
    result: dict[str, Any],
    llm_cfg: dict[str, Any],
    source_text: str,
    game_name: str,
    tags: list[str],
) -> dict[str, Any]:
    normalized = dict(result or {})
    normalized = _normalize_llm_result(normalized, game_name, tags)
    normalized["body_html"] = _sanitize_generated_html(normalized.get("body_html", ""))
    normalized["body_html"] = _ensure_question_answer_pairs(
        normalized.get("body_html", ""),
        game_name=game_name,
    )

    audit = _audit_article_quality(
        title=normalized.get("title", ""),
        body_html=normalized.get("body_html", ""),
    )
    repaired = False
    repair_mode = "none"

    if audit["failed_rules"]:
        repaired_result = _repair_with_llm_if_needed(
            llm_cfg=llm_cfg,
            source_text=source_text,
            game_name=game_name,
            tags=tags,
            current_result=normalized,
            audit=audit,
        )
        if repaired_result:
            normalized = _normalize_llm_result(repaired_result, game_name, tags)
            normalized["body_html"] = _sanitize_generated_html(normalized.get("body_html", ""))
            normalized["body_html"] = _ensure_question_answer_pairs(
                normalized.get("body_html", ""),
                game_name=game_name,
            )
            audit_after_llm = _audit_article_quality(
                title=normalized.get("title", ""),
                body_html=normalized.get("body_html", ""),
            )
            if len(audit_after_llm["failed_rules"]) <= len(audit["failed_rules"]):
                audit = audit_after_llm
                repaired = True
                repair_mode = "llm_repair"

    if audit["failed_rules"]:
        normalized["body_html"] = _rule_based_repair_html(
            body_html=normalized.get("body_html", ""),
            game_name=game_name,
            source_text=source_text,
            tags=tags,
        )
        normalized["title"] = _apply_text_guardrails(normalized.get("title", ""))
        normalized["meta_title"] = _apply_text_guardrails(normalized.get("meta_title", ""))
        normalized["meta_description"] = _apply_text_guardrails(normalized.get("meta_description", ""))
        normalized["body_html"] = _ensure_question_answer_pairs(
            normalized.get("body_html", ""),
            game_name=game_name,
        )
        audit = _audit_article_quality(
            title=normalized.get("title", ""),
            body_html=normalized.get("body_html", ""),
        )
        repaired = True
        repair_mode = "rule_repair"

    diagnostics = dict(normalized.get("diagnostics") or {})
    diagnostics["quality_audit"] = audit
    diagnostics["quality_repaired"] = repaired
    diagnostics["quality_repair_mode"] = repair_mode
    normalized["diagnostics"] = diagnostics
    return normalized


def _sanitize_generated_html(body_html: str) -> str:
    value = str(body_html or "")
    value = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", value)
    value = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", value)
    value = re.sub(r"(?is)<blockquote[^>]*>.*?</blockquote>", " ", value)
    value = re.sub(r"(?is)<img\b[^>]*>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    for pattern in _FORUM_NOISE_PATTERNS:
        value = re.sub(pattern, " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return _apply_html_guardrails(value)


def _ensure_question_answer_pairs(body_html: str, *, game_name: str) -> str:
    html = str(body_html or "")
    answer_tpl = (
        "<p>A{num}：建議先依照 {game} 目前版本主流配置調整，"
        "並在投入資源前完成區服、角色與商品資訊核對，可大幅降低風險。</p>"
    )

    missing_answer_after_q = re.compile(
        r"(?is)(<p[^>]*>\s*Q\s*(\d+)\s*[:：].*?</p>)(\s*)(?=(<p[^>]*>\s*Q\s*\d+\s*[:：]|<h[1-6]\b|<table\b|$))"
    )
    html = missing_answer_after_q.sub(
        lambda m: m.group(1)
        + m.group(3)
        + answer_tpl.format(num=m.group(2), game=escape(game_name)),
        html,
    )

    missing_answer_after_h = re.compile(
        r"(?is)(<h[23][^>]*>\s*Q\s*(\d+)\s*[:：].*?</h[23]>)(\s*)(?=(<h[23]\b|<table\b|$))"
    )
    html = missing_answer_after_h.sub(
        lambda m: m.group(1)
        + m.group(3)
        + answer_tpl.format(num=m.group(2), game=escape(game_name)),
        html,
    )

    return html


def _audit_article_quality(*, title: str, body_html: str) -> dict[str, Any]:
    title_text = str(title or "").strip()
    html = str(body_html or "")
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain).strip()

    h1_count = len(re.findall(r"(?is)<h1\b[^>]*>", html))
    h2_count = len(re.findall(r"(?is)<h2\b[^>]*>", html))
    h3_count = len(re.findall(r"(?is)<h3\b[^>]*>", html))
    table_count = len(re.findall(r"(?is)<table\b", html))
    intro_match = re.search(r"(?is)<p[^>]*>(.*?)</p>", html)
    intro_text = re.sub(r"<[^>]+>", " ", intro_match.group(1) if intro_match else "")
    intro_text = re.sub(r"\s+", " ", intro_text).strip()

    failed_rules: list[str] = []
    if not title_text:
        failed_rules.append("missing_title")
    if h1_count < 1:
        failed_rules.append("missing_h1")
    if h2_count < _QUALITY_MIN_H2:
        failed_rules.append("insufficient_h2")
    if h3_count < _QUALITY_MIN_H3:
        failed_rules.append("insufficient_h3")
    if table_count < 1:
        failed_rules.append("missing_table")
    if len(plain) < _QUALITY_MIN_TEXT_LEN:
        failed_rules.append("text_too_short")
    if len(intro_text) < 80:
        failed_rules.append("intro_too_short")

    forbidden_hits = []
    for word, _replacement in _BANNED_WORD_REPLACEMENTS:
        if word in title_text or word in plain:
            forbidden_hits.append(word)
    if forbidden_hits:
        failed_rules.append("forbidden_words")

    return {
        "title_len": len(title_text),
        "text_len": len(plain),
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "table_count": table_count,
        "intro_len": len(intro_text),
        "failed_rules": failed_rules,
        "forbidden_hits": forbidden_hits,
        "passed": not failed_rules,
    }


def _repair_with_llm_if_needed(
    *,
    llm_cfg: dict[str, Any],
    source_text: str,
    game_name: str,
    tags: list[str],
    current_result: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any] | None:
    api_key = str(llm_cfg.get("api_key") or "").strip()
    if not api_key:
        return None

    failed_rules = ", ".join(audit.get("failed_rules") or [])
    prompt = (
        "請修復以下 SEO 攻略文章，使其達到發布標準。\n"
        "規則：\n"
        "1) 台灣繁體中文、玩家口吻。\n"
        "2) HTML 結構含 1 個 <h1>、至少 3 個 <h2>、至少 2 個 <h3>。\n"
        "3) 開頭導語 120-220 字；全文目標約 1000 字。\n"
        "4) 文末必須有 2 欄重點表格。\n"
        "5) 禁用詞：全方位、解析、全面、指南、高效。\n"
        "6) 可保留有價值連結，移除論壇噪音和留言語氣。\n"
        "7) 僅輸出 JSON，鍵名：title, body_html, tags, meta_description, meta_title。\n\n"
        f"遊戲名稱：{game_name}\n"
        f"關鍵詞：{'、'.join(tags[:12])}\n"
        f"未通過規則：{failed_rules}\n"
        "目前文章 JSON：\n"
        f"{json.dumps(current_result, ensure_ascii=False)}\n\n"
        "來源原文：\n"
        f"{source_text}"
    )

    try:
        if llm_cfg.get("style") == "gemini_generate_content":
            url = _build_gemini_generate_content_url(
                base_url=str(llm_cfg.get("base_url") or DEFAULT_POLO_BASE_URL),
                model=str(llm_cfg.get("model") or DEFAULT_POLO_MODEL),
            )
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": prompt}]},
                ]
            }
            response = _post_with_auth_variants(
                url=url,
                payload=payload,
                api_key=api_key,
                timeout_seconds=int(llm_cfg.get("timeout_seconds") or 45),
                prefer_bearer=False,
            )
            response.raise_for_status()
            content = _extract_gemini_text(response.json())
        else:
            url = _build_openai_chat_url(base_url=str(llm_cfg.get("base_url") or DEFAULT_OPENAI_BASE_URL))
            payload = {
                "model": str(llm_cfg.get("model") or DEFAULT_OPENAI_MODEL),
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "你是資深遊戲編輯。只輸出 JSON。"},
                    {"role": "user", "content": prompt},
                ],
            }
            response = _post_with_auth_variants(
                url=url,
                payload=payload,
                api_key=api_key,
                timeout_seconds=int(llm_cfg.get("timeout_seconds") or 45),
                prefer_bearer=True,
            )
            response.raise_for_status()
            content = _extract_openai_content(response.json())

        parsed = _extract_json_object(content)
        if not isinstance(parsed, dict):
            return None
        return parsed
    except Exception as exc:
        logger.warning("quality repair with llm failed: %s", exc)
        return None


def _rule_based_repair_html(*, body_html: str, game_name: str, source_text: str, tags: list[str]) -> str:
    source_lines = _extract_meaningful_lines(source_text)
    if not source_lines:
        source_lines = [
            f"{game_name} 最近版本節奏變化",
            f"{game_name} 實戰配置建議",
            f"{game_name} 儲值流程與安全提醒",
        ]

    intro = (
        f"這篇會用玩家視角整理 {game_name} 現在最該注意的版本重點、養成節奏和儲值安全流程。"
        "你可以直接照著段落走，先把每天必做和資源投入順序穩住，再補強細節，避免白白浪費時間與素材。"
    )
    highlights = source_lines[:5]
    highlight_html = "".join(f"<li>{escape(line)}</li>" for line in highlights)
    keywords_text = "、".join(tags[:6]) if tags else game_name

    repaired_html = (
        f"<h1>{escape(game_name)} 版本重點與實戰整理</h1>"
        f"<p>{escape(intro)}</p>"
        "<h2>版本重點速覽 ↗</h2>"
        "<h3>先看這幾件事</h3>"
        f"<ul>{highlight_html}</ul>"
        "<h2>養成與實戰路線 ●</h2>"
        "<h3>資源投入順序</h3>"
        "<p>先把主力角色的核心裝備與技能位補齊，再依活動時程補強副位。"
        "這樣能在最少資源下換到最穩定的戰力提升，打本與推圖都比較順。</p>"
        "<h3>活動週期打法</h3>"
        "<p>活動前先預留材料，活動期間優先做高回報任務和限時兌換，"
        "低回報項目先放掉，避免體力與貨幣被零散消耗。</p>"
        "<h2>儲值流程與安全提醒 ⭐</h2>"
        "<p>儲值前務必核對區服、角色資訊與商品面額，付款後保留訂單憑證。"
        "若遇到異常延遲，先用憑證回報客服，不要重複下單。</p>"
        "<h2>常見問題</h2>"
        "<h3>新手第一天該先做什麼？</h3>"
        "<p>先完成主線和新手任務，把基礎資源池打開，再挑一條主流流派深入培養，"
        "不要一開始就同時分散培養多條線。</p>"
        "<h3>怎麼避免養成方向走歪？</h3>"
        "<p>每次版本更新後先確認主流配裝與技能優先級，再調整你的素材投放比例，"
        "保持主軸明確，成長速度會快很多。</p>"
        "<h2>整理小表格</h2>"
        "<table><thead><tr><th>項目</th><th>建議</th></tr></thead><tbody>"
        "<tr><td>每日優先</td><td>主線、活動高回報任務先清</td></tr>"
        "<tr><td>資源分配</td><td>主力先滿，副位後補</td></tr>"
        "<tr><td>儲值檢查</td><td>區服/角色/面額三次核對</td></tr>"
        "<tr><td>關鍵詞</td><td>"
        f"{escape(keywords_text)}"
        "</td></tr>"
        "</tbody></table>"
    )

    plain_len = len(re.sub(r"<[^>]+>", " ", repaired_html))
    if plain_len < _QUALITY_MIN_TEXT_LEN:
        repaired_html += (
            "<h2>進階補充</h2>"
            "<p>如果你每天在線時間有限，建議把任務拆成「保底進度」和「進階提升」兩段。"
            "平日先完成保底，週末再集中刷進階內容，整體效率和壓力會更平衡。"
            "另外，記得定期回看版本公告與玩家社群的實測回饋，"
            "把你目前的配裝和資源規劃做小幅校正，長期下來可以少走很多冤枉路。</p>"
        )

    return _apply_html_guardrails(repaired_html)

def _build_basic_html(game_name: str, lines: list[str]) -> str:
    lead = (
        lines[0]
        if lines
        else (
            f"最近不少玩家都在討論 {game_name} 的版本節奏、資源分配和儲值效率，"
            "這篇會用玩家視角把重點拆開講清楚。"
        )
    )
    highlights = lines[1:5] if len(lines) > 1 else [
        f"{game_name} 近期版本強勢玩法變化",
        "新手與回鍋玩家優先處理的養成順序",
        "活動期間資源投入與回收效率",
        "儲值與代儲最容易踩雷的環節",
    ]
    faq_seed = lines[5:7] if len(lines) > 5 else [
        "代儲會不會影響帳號安全？",
        "為什麼不同儲值管道價格會不一樣？",
    ]

    list_items = "".join(f"<li>{escape(item)}</li>" for item in highlights)
    faq_1 = escape(faq_seed[0] if faq_seed else "代儲會不會影響帳號安全？")
    faq_2 = escape(faq_seed[1] if len(faq_seed) > 1 else "為什麼不同儲值管道價格會不一樣？")

    return (
        f"<h1>{escape(game_name)} 版本重點與代儲實戰整理</h1>"
        f"<p>{escape(lead)}</p>"
        "<h2>版本重點速覽 ↗</h2>"
        "<h3>先看這四件事</h3>"
        f"<ul>{list_items}</ul>"
        "<h2>實戰與養成建議 ●</h2>"
        "<h3>資源怎麼投比較穩</h3>"
        "<p>先鎖定主力隊伍與關鍵素材，再依照活動週期做投入，避免資源分散導致戰力成長停滯。</p>"
        "<h3>活動期間怎麼打比較順</h3>"
        "<p>優先完成高回報任務與限時兌換，低性價比項目可以延後，確保體力與貨幣花在關鍵節點。</p>"
        "<h2>代儲流程與安全提醒 ⭐</h2>"
        "<p>儲值前先確認區服、角色 ID、商品面額與付款資訊；完成付款後記得保留憑證，方便客服快速核單。</p>"
        "<h2>常見問題</h2>"
        f"<h3>{faq_1}</h3>"
        "<p>只要走正規流程、避開來路不明的低價管道，並開啟帳號安全驗證，風險就能大幅降低。</p>"
        f"<h3>{faq_2}</h3>"
        "<p>價格差通常來自匯率、活動補貼、支付成本與到帳速度，不一定代表不安全，但還是要先核對管道評價。</p>"
        "<h2>整理小表格</h2>"
        "<table><thead><tr><th>項目</th><th>建議</th></tr></thead><tbody>"
        "<tr><td>版本開荒</td><td>先定主隊，再補關鍵素材</td></tr>"
        "<tr><td>活動資源</td><td>優先高回報兌換，避免分散投入</td></tr>"
        "<tr><td>代儲流程</td><td>先核對區服與角色，再付款並留憑證</td></tr>"
        "<tr><td>帳號安全</td><td>開啟驗證機制，不使用異常低價來源</td></tr>"
        "</tbody></table>"
    )

def _build_tags(game_name: str, custom_keywords: list[str] | None) -> list[str]:
    base_tags = [
        game_name,
        f"{game_name} 攻略",
        f"{game_name} 儲值",
        f"{game_name} 代儲",
        f"{game_name} 充值",
        "手遊代儲",
        "儲值安全",
        "遊戲充值",
    ]
    if custom_keywords:
        base_tags.extend(custom_keywords)
    return [_apply_text_guardrails(tag) for tag in _dedupe_tags(base_tags)]

def _contains_html_tag(text: str) -> bool:
    return bool(re.search(r"<[a-zA-Z][^>]*>", text or ""))


def _coerce_plain_text_to_html(raw: str, game_name: str) -> str:
    cleaned = (raw or "").strip()
    if not cleaned:
        return _build_basic_html(game_name, [])

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return _build_basic_html(game_name, [])

    paragraphs = "".join(f"<p>{escape(line)}</p>" for line in lines[:18])
    return (
        f"<h1>{escape(game_name)} 儲值與玩法整理</h1>"
        "<h2>重點內容</h2>"
        f"{paragraphs}"
    )

def _dedupe_tags(tags: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for tag in tags:
        item = str(tag).strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _apply_text_guardrails(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    for banned, replacement in _BANNED_WORD_REPLACEMENTS:
        cleaned = cleaned.replace(banned, replacement)
    return cleaned


def _apply_html_guardrails(body_html: str) -> str:
    value = str(body_html or "")
    for banned, replacement in _BANNED_WORD_REPLACEMENTS:
        value = value.replace(banned, replacement)
    return value


def _looks_like_garbled_text(text: str) -> bool:
    value = str(text or "").strip()
    if not value:
        return False
    if _GARBLED_REPLACEMENT_CHAR in value:
        return True
    if _GARBLED_QMARK_PATTERN.search(value):
        return True
    if "???" in value:
        return True
    return False


def _repair_garbled_text(text: str, *, game_name: str, fallback: str) -> str:
    value = str(text or "").strip()
    if not value:
        return fallback

    value = value.replace(_GARBLED_REPLACEMENT_CHAR, " ")
    if _GARBLED_QMARK_PATTERN.search(value):
        replacement = game_name.strip() or "這款遊戲"
        value = _GARBLED_QMARK_PATTERN.sub(replacement, value)
    value = re.sub(r"\s+", " ", value).strip()
    value = _apply_text_guardrails(value)

    if _looks_like_garbled_text(value):
        return _apply_text_guardrails(str(fallback or "").strip())
    return value


def _repair_garbled_html(body_html: str, *, game_name: str) -> str:
    value = str(body_html or "")
    if not value:
        return value

    replacement = escape(game_name.strip() or "這款遊戲")
    value = value.replace(_GARBLED_REPLACEMENT_CHAR, " ")
    value = _GARBLED_QMARK_PATTERN.sub(replacement, value)
    return value


def _extract_meaningful_lines(raw_text: str) -> list[str]:
    if not raw_text:
        return []

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip(" -*\u2022\t") for line in text.split("\n")]

    clean_lines: list[str] = []
    for line in lines:
        if not line:
            continue
        if len(line) < 6:
            continue
        if _is_noise_line(line):
            continue
        if _is_forum_noise_line(line):
            continue
        if line not in clean_lines:
            clean_lines.append(line)

    return clean_lines[:30]


def _is_noise_line(line: str) -> bool:
    if re.fullmatch(r"https?://\S+", line):
        return True
    if re.fullmatch(r"[\W_]+", line):
        return True
    if re.fullmatch(r"[\U0001F300-\U0001FAFF\s]+", line):
        return True
    return False


def _is_forum_noise_line(line: str) -> bool:
    text = str(line or "").strip()
    if not text:
        return True

    for pattern in _FORUM_NOISE_PATTERNS:
        if re.search(pattern, text):
            return True

    if re.fullmatch(r"\d+\s*[Ff樓楼]\s*.*", text):
        return True
    if re.fullmatch(r"(?:\+|-)?\d+\s*(?:GP|BP)?", text, flags=re.I):
        return True
    if len(re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", text)) < 4:
        return True
    return False


def _first_non_empty(*values: str) -> str:
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _coerce_positive_int(value: Any, default: int = 45) -> int:
    try:
        number = int(value)
        if number > 0:
            return number
    except Exception:
        pass
    return int(default)


def _load_google_api_config() -> dict[str, Any]:
    """
    Bahamut crawler style config file.

    Expected json keys:
    - api_key
    - base_url
    - model
    """
    candidates = [
        Path(__file__).resolve().parents[1] / "google_api_config.json",
        Path(__file__).resolve().parents[2] / "google_api_config.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception as exc:
            logger.warning("Failed to read %s: %s", path, exc)
            continue
    return {}


def _format_llm_error(exc: Exception) -> str:
    if isinstance(exc, requests.HTTPError):
        response = getattr(exc, "response", None)
        if response is not None:
            body = (response.text or "").strip().replace("\n", " ")
            if len(body) > 300:
                body = body[:300]
            return f"http_{response.status_code}: {body}"
    return str(exc)



