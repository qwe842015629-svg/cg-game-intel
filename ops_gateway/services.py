from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import random
import re
import shlex
import subprocess
import threading
import time
from difflib import SequenceMatcher
from html import escape, unescape
from typing import Any, Callable
from urllib.parse import quote, urlparse

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, When
from django.utils import timezone

from .models import OperationApproval, OperationAuditLog

try:
    from .bahamut_ranking import (
        resolve_bahamut_bsn_for_game_title,
        search_bahamut_entries,
        select_bahamut_entries_for_daily,
    )
except Exception:  # pragma: no cover - optional module for local/dev snapshots
    resolve_bahamut_bsn_for_game_title = None
    search_bahamut_entries = None
    select_bahamut_entries_for_daily = None


User = get_user_model()

_REQUEST_TIMEOUT = 20
_LONG_TOKEN_RE = re.compile(r"[A-Za-z0-9_/\-=]{80,}")
_SOCIAL_DOMAIN_HINTS: dict[str, str] = {
    "facebook.com": "facebook",
    "discord.com": "discord",
    "discord.gg": "discord",
    "x.com": "x",
    "twitter.com": "x",
    "instagram.com": "instagram",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "tiktok.com": "tiktok",
    "reddit.com": "reddit",
    "twitch.tv": "twitch",
    "line.me": "line",
}
_SOCIAL_LABELS: dict[str, str] = {
    "facebook": "Facebook",
    "discord": "Discord",
    "x": "X",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "reddit": "Reddit",
    "twitch": "Twitch",
    "line": "LINE",
}
_SKIP_EXTERNAL_HOST_PARTS = (
    "play.google.com",
    "google.com",
    "googleusercontent.com",
    "gstatic.com",
    "ggpht.com",
    "googleadservices.com",
    "googlesyndication.com",
    "doubleclick.net",
    "ytimg.com",
    "android.com",
    "apps.apple.com",
    "itunes.apple.com",
    "forum.gamer.com.tw",
    "gamer.com.tw",
    "w3.org",
    "schema.org",
)
_COMMON_LINK_TOKENS = {
    "com",
    "net",
    "org",
    "www",
    "app",
    "apps",
    "game",
    "games",
    "gaming",
    "global",
    "mobile",
    "android",
    "ios",
    "official",
    "studio",
    "interactive",
    "company",
    "international",
    "server",
    "play",
    "google",
}
_OVERVIEW_NOISE_HINTS = (
    "http://",
    "https://",
    "客服",
    "客戶",
    "客户",
    "聯繫",
    "联系",
    "隱私",
    "隐私",
    "條款",
    "条款",
    "協議",
    "协议",
    "年齡",
    "年龄",
    "下載",
    "下载",
    "instagram",
    "youtube",
    "facebook",
    "twitter",
    "discord",
    "tiktok",
    "google play",
    "app store",
    "moonton.com",
)
_GOOGLE_PLAY_DISCOVERY_SEEDS = (
    "https://play.google.com/store/apps/category/GAME?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/category/GAME_ACTION?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/category/GAME_ADVENTURE?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/category/GAME_ROLE_PLAYING?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/category/GAME_STRATEGY?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/category/SOCIAL?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/collection/topselling_free?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/collection/new_free?hl=zh_TW&gl=TW",
    "https://play.google.com/store/apps/top/category/GAME?hl=zh_TW&gl=TW",
    "https://play.google.com/store/search?q=game&c=apps&hl=zh_TW&gl=TW",
    "https://play.google.com/store/search?q=social+game&c=apps&hl=zh_TW&gl=TW",
)
_GOOGLE_PLAY_ID_RE = re.compile(
    r"(?:/store/apps/details\?id=|https?://play\.google\.com/store/apps/details\?id=)([A-Za-z0-9._]+)",
    flags=re.I,
)
_DAILY_ARTICLE_TOPIC_PLAN: list[tuple[str, list[str]]] = [
    ("兑换码", ["兑换码", "礼包码", "redeem code", "可用码"]),
    ("游戏攻略", ["新手攻略", "进阶攻略", "阵容推荐", "玩法技巧"]),
    ("版本更新", ["版本更新", "更新公告", "平衡改动", "patch notes"]),
    ("近期活动", ["近期活动", "限时活动", "活动日历", "联动活动"]),
    ("福利规划", ["福利规划", "资源规划", "白嫖路线", "每日必做"]),
    ("综合资讯", ["资讯汇总", "重点提醒", "常见问题", "实战建议"]),
]


def create_audit_log(
    *,
    approval: OperationApproval,
    event_type: str,
    actor=None,
    actor_name: str = "",
    client_id: str = "",
    client_ip: str = "",
    request_snapshot: dict[str, Any] | None = None,
    result_snapshot: dict[str, Any] | None = None,
    message: str = "",
) -> OperationAuditLog:
    return OperationAuditLog.objects.create(
        approval=approval,
        event_type=event_type,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        actor_name=actor_name or (getattr(actor, "username", "") if actor else ""),
        client_id=client_id,
        client_ip=client_ip,
        request_snapshot=request_snapshot or {},
        result_snapshot=result_snapshot or {},
        message=message or "",
    )


def execute_approval(approval: OperationApproval, actor=None) -> dict[str, Any]:
    if approval.action == OperationApproval.ACTION_SEO_ARTICLE_PUBLISH:
        return _execute_seo_article_publish(approval, actor=actor)
    if approval.action == OperationApproval.ACTION_DAILY_ROBOT_RUN:
        return _execute_daily_robot_run(approval, actor=actor)
    if approval.action == OperationApproval.ACTION_SERVER_TASK_EXEC:
        return _execute_server_task_exec(approval, actor=actor)
    raise ValueError(f"Unsupported action: {approval.action}")


def _execute_daily_robot_run(approval: OperationApproval, actor=None) -> dict[str, Any]:
    from .auto_runner import run_daily_cycle_now

    payload = approval.payload or {}
    force = bool(payload.get("force", True))
    trigger_source = str(payload.get("trigger_source") or "approval_manual")[:32] or "approval_manual"

    result = run_daily_cycle_now(force=force, trigger_source=trigger_source)
    status_value = str(result.get("status") or "").strip().lower()
    if status_value in {"failed", "db_not_ready"}:
        raise ValueError(f"daily_robot_run failed: {result}")

    return {
        "force": force,
        "trigger_source": trigger_source,
        "daily_run": result,
    }


def _execute_seo_article_publish(approval: OperationApproval, actor=None) -> dict[str, Any]:
    from seo_automation.models import SeoArticle
    from seo_automation.views import _publish_seo_article, _refresh_seo_article_source_and_media

    payload = approval.payload or {}
    seo_article_id = payload.get("seo_article_id") or approval.target_id
    if not seo_article_id:
        raise ValueError("payload.seo_article_id is required")

    try:
        seo_article_id_int = int(seo_article_id)
    except Exception as exc:
        raise ValueError("seo_article_id must be an integer") from exc

    seo_article = (
        SeoArticle.objects.select_related("task", "published_article")
        .filter(pk=seo_article_id_int)
        .first()
    )
    if not seo_article:
        raise ValueError(f"SeoArticle({seo_article_id_int}) not found")

    run_step5 = bool(payload.get("run_step5", True))
    publish_now = bool(payload.get("publish_now", False))
    publish_at = payload.get("publish_at")

    quality_result = None
    if run_step5:
        quality_result = _refresh_seo_article_source_and_media(
            seo_article=seo_article,
            task_keyword=seo_article.task.keyword if seo_article.task else "",
            request_user=actor,
        )
        seo_article.refresh_from_db()

    article = _publish_seo_article(
        seo_article=seo_article,
        request_user=actor,
        publish_now=publish_now,
        publish_at=publish_at,
    )
    seo_article.refresh_from_db()

    return {
        "seo_article_id": seo_article.id,
        "article_id": article.id,
        "seo_status": seo_article.status,
        "publish_now": publish_now,
        "publish_at": seo_article.publish_at.isoformat() if seo_article.publish_at else None,
        "run_step5": run_step5,
        "quality": quality_result or {},
    }


def mark_approval_executed(approval: OperationApproval, *, result: dict[str, Any], actor=None) -> OperationApproval:
    approval.status = OperationApproval.STATUS_EXECUTED
    approval.executed_by = actor if getattr(actor, "is_authenticated", False) else None
    approval.executed_at = timezone.now()
    approval.failed_at = None
    approval.error_message = ""
    approval.last_result = result or {}
    approval.save(
        update_fields=[
            "status",
            "executed_by",
            "executed_at",
            "failed_at",
            "error_message",
            "last_result",
            "updated_at",
        ]
    )
    return approval


def mark_approval_failed(approval: OperationApproval, *, error_message: str) -> OperationApproval:
    approval.status = OperationApproval.STATUS_FAILED
    approval.failed_at = timezone.now()
    approval.error_message = (error_message or "")[:2000]
    approval.save(update_fields=["status", "failed_at", "error_message", "updated_at"])
    return approval


_DEFAULT_SERVER_TASK_CATALOG: dict[str, dict[str, Any]] = {
    "backend_check": {
        "description": "Run Django health check",
        "command": "cd /var/www/cypher_backend && venv/bin/python manage.py check",
        "timeout_seconds": 300,
        "risk_level": 2,
    },
    "backend_restart_gunicorn": {
        "description": "Restart Gunicorn service",
        "command": "sudo systemctl restart gunicorn && sudo systemctl is-active gunicorn",
        "timeout_seconds": 120,
        "risk_level": 4,
    },
    "backend_tail_gunicorn": {
        "description": "Show recent Gunicorn logs",
        "command": "sudo journalctl -u gunicorn --no-pager -n 80",
        "timeout_seconds": 120,
        "risk_level": 1,
    },
    "backend_git_pull": {
        "description": "Pull latest backend code",
        "command": "cd /var/www/cypher_backend && git pull --ff-only",
        "timeout_seconds": 240,
        "risk_level": 3,
    },
}


def _coerce_positive_int(value: Any, default: int, *, minimum: int = 1, maximum: int = 3600) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return max(minimum, min(maximum, parsed))


def _normalize_server_task_spec(key: str, spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict):
        return {}

    task_key = str(key or "").strip()
    command = str(spec.get("command") or "").strip()
    if not task_key or not command:
        return {}

    cwd = str(spec.get("cwd") or "").strip()
    description = str(spec.get("description") or task_key).strip() or task_key
    timeout_seconds = _coerce_positive_int(spec.get("timeout_seconds"), 300, minimum=10, maximum=3600)
    risk_level = _coerce_positive_int(spec.get("risk_level"), 3, minimum=1, maximum=5)

    return {
        "task_key": task_key,
        "description": description,
        "command": command,
        "cwd": cwd,
        "timeout_seconds": timeout_seconds,
        "risk_level": risk_level,
    }


def get_server_task_catalog() -> dict[str, dict[str, Any]]:
    raw = getattr(settings, "FEISHU_OPS_TASKS", {})
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = {}

    normalized: dict[str, dict[str, Any]] = {}
    source = raw if isinstance(raw, dict) and raw else _DEFAULT_SERVER_TASK_CATALOG
    for key, spec in source.items():
        row = _normalize_server_task_spec(str(key or "").strip(), spec)
        if row:
            normalized[row["task_key"]] = row
    return normalized


def _render_task_command(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    command_tpl = str(spec.get("command") or "").strip()
    if not command_tpl:
        return ""

    tokens = payload.get("args_tokens")
    if not isinstance(tokens, list):
        raw_args = str(payload.get("args") or "").strip()
        tokens = [item for item in shlex.split(raw_args) if str(item).strip()] if raw_args else []

    safe_args = " ".join(shlex.quote(str(item)) for item in tokens if str(item).strip())
    if "{args}" in command_tpl:
        return command_tpl.replace("{args}", safe_args)
    if safe_args:
        return f"{command_tpl} {safe_args}".strip()
    return command_tpl


def _is_shell_command_allowed(command: str) -> bool:
    allowed = [
        str(item).strip()
        for item in (getattr(settings, "FEISHU_OPS_SHELL_ALLOWED_PREFIXES", []) or [])
        if str(item).strip()
    ]
    if not allowed:
        return False

    if "*" in allowed or "__all__" in allowed:
        return True

    try:
        parts = shlex.split(str(command or "").strip())
    except Exception:
        return False
    if not parts:
        return False
    first = str(parts[0] or "").strip()
    if not first:
        return False

    for prefix in allowed:
        if first == prefix or first.startswith(prefix):
            return True
    return False


def _execute_server_task_exec(approval: OperationApproval, actor=None) -> dict[str, Any]:
    payload = approval.payload or {}
    task_key = str(payload.get("task_key") or approval.target_id or "").strip()
    if not task_key:
        raise ValueError("payload.task_key is required")

    spec: dict[str, Any]
    if task_key == "__shell__":
        if not bool(getattr(settings, "FEISHU_OPS_SHELL_ENABLED", False)):
            raise ValueError("custom shell command is disabled")
        command = str(payload.get("shell_command") or "").strip()
        if not command:
            raise ValueError("payload.shell_command is required")
        if not _is_shell_command_allowed(command):
            raise ValueError("shell command prefix not allowed")
        spec = {
            "description": "custom shell command",
            "command": command,
            "cwd": str(payload.get("cwd") or "").strip(),
            "timeout_seconds": _coerce_positive_int(payload.get("timeout_seconds"), 300),
        }
    else:
        catalog = get_server_task_catalog()
        spec = catalog.get(task_key) or {}
        if not spec:
            raise ValueError(f"server task not found: {task_key}")

    if task_key == "__shell__":
        command = str(spec.get("command") or "").strip()
    else:
        command = _render_task_command(spec, payload)
    if not command:
        raise ValueError(f"server task command empty: {task_key}")

    cwd = str(payload.get("cwd") or spec.get("cwd") or "").strip() or None
    timeout_seconds = _coerce_positive_int(payload.get("timeout_seconds") or spec.get("timeout_seconds"), 300)

    started = time.time()
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"server task timeout after {timeout_seconds}s: {task_key}") from exc

    duration_ms = int((time.time() - started) * 1000)
    stdout_text = str(completed.stdout or "")[-5000:]
    stderr_text = str(completed.stderr or "")[-3000:]

    result = {
        "task_key": task_key,
        "description": str(spec.get("description") or task_key),
        "command": command,
        "cwd": cwd or "",
        "timeout_seconds": timeout_seconds,
        "returncode": int(completed.returncode),
        "duration_ms": duration_ms,
        "stdout": stdout_text,
        "stderr": stderr_text,
    }

    if completed.returncode != 0:
        err = stderr_text.strip() or stdout_text.strip() or "unknown error"
        raise ValueError(f"server task failed rc={completed.returncode}: {err[:300]}")

    return result

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _run_callable_with_wall_timeout(
    func: Callable[[], Any],
    *,
    timeout_seconds: int,
) -> tuple[str, Any, str, int]:
    result_box: dict[str, Any] = {}
    error_box: dict[str, str] = {}
    done = threading.Event()
    started = time.monotonic()

    def _target() -> None:
        try:
            result_box["value"] = func()
        except Exception as exc:
            error_box["error"] = str(exc)
        finally:
            done.set()

    worker = threading.Thread(target=_target, name="ops-gateway-wall-timeout", daemon=True)
    worker.start()
    finished = done.wait(timeout=max(1, int(timeout_seconds)))
    elapsed_ms = int((time.monotonic() - started) * 1000)

    if not finished:
        return "timeout", None, f"wall_timeout_{int(timeout_seconds)}s", elapsed_ms
    if "error" in error_box:
        return "error", None, str(error_box.get("error") or "unknown_error"), elapsed_ms
    return "ok", result_box.get("value"), "", elapsed_ms


def _normalize_publish_status(status: Any, *, fallback_publish_now: bool = True) -> str:
    value = str(status or "").strip().lower()
    if value in {"published", "draft"}:
        return value
    return "published" if bool(fallback_publish_now) else "draft"


def _strip_html(value: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", value or "", flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_text_block(value: str) -> str:
    text = str(value or "")
    text = text.replace("\uFFFD", " ")
    text = text.replace("\x00", " ")
    text = re.sub(r"\?{3,}", " ", text)
    text = re.sub(r"\s*\|\s*", " | ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _contains_long_token(text: str, *, min_len: int = 80) -> bool:
    if not text:
        return False
    return bool(re.search(rf"[A-Za-z0-9_/\-=]{{{max(20, min_len)},}}", text))


def _looks_garbled_text(text: str) -> bool:
    plain = _clean_text_block(text)
    if not plain:
        return True
    if _contains_long_token(plain, min_len=90):
        return True
    if len(plain) >= 140:
        ascii_like = sum(1 for ch in plain if ch.isascii() and (ch.isalnum() or ch in "_-/= "))
        if ascii_like / max(1, len(plain)) >= 0.88 and plain.count(" ") <= 3:
            return True
    return False


def _sanitize_import_text(value: str, *, fallback: str = "") -> str:
    raw = _clean_text_block(value)
    cleaned = _LONG_TOKEN_RE.sub(" ", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned and not _looks_garbled_text(cleaned):
        return cleaned

    fb = _clean_text_block(fallback)
    fb = _LONG_TOKEN_RE.sub(" ", fb)
    fb = re.sub(r"\s+", " ", fb).strip()
    if fb and not _looks_garbled_text(fb):
        return fb
    return fb or cleaned or ""


def _normalize_topup_template_content(value: str) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    text = re.sub(r"(!\[[^\]]*\]\()media/", r"\1/media/", text, flags=re.I)
    text = re.sub(r"(!\[[^\]]*\]\()uploads/", r"\1/media/uploads/", text, flags=re.I)
    text = re.sub(r'(<img[^>]+src=["\'])media/', r"\1/media/", text, flags=re.I)
    text = re.sub(r'(<img[^>]+src=["\'])uploads/', r"\1/media/uploads/", text, flags=re.I)
    return text


def _build_import_i18n_map(
    *,
    default_text: str,
    tw_text: str = "",
    existing_map: Any = None,
) -> dict[str, str]:
    primary = str(default_text or "").strip()
    secondary_tw = str(tw_text or primary).strip() or primary
    locale_keys = ["zh-CN", "zh-TW", "en", "ja", "ko", "fr", "de", "vi", "th"]
    if isinstance(existing_map, dict):
        for raw_key in existing_map.keys():
            key = str(raw_key or "").strip()
            if key and key not in locale_keys:
                locale_keys.append(key)

    mapped: dict[str, str] = {}
    for locale_key in locale_keys:
        mapped[locale_key] = secondary_tw if locale_key == "zh-TW" else primary
    return mapped


def _normalize_for_similarity(value: str) -> str:
    plain = _strip_html(value).lower()
    plain = re.sub(r"[\W_]+", " ", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _engagement_score(article) -> int:
    if article is None:
        return 0
    return (
        _safe_int(getattr(article, "view_count", 0))
        + _safe_int(getattr(article, "like_count", 0)) * 5
        + _safe_int(getattr(article, "comment_count", 0)) * 8
    )


def _extract_urls_from_html(raw_html: str) -> list[str]:
    if not raw_html:
        return []
    normalized = (
        str(raw_html)
        .replace("\\/", "/")
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("&amp;", "&")
    )
    candidates = re.findall(r"https?://[^\s\"'<>]+", normalized, flags=re.I)
    seen: set[str] = set()
    urls: list[str] = []
    for item in candidates:
        value = item.strip().rstrip("),.;")
        while value.endswith(")") and value.count("(") < value.count(")"):
            value = value[:-1]
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        urls.append(value)
    return urls


def _tokenize_link_relevance(value: str) -> list[str]:
    raw = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
    if not raw:
        return []
    tokens: list[str] = []
    for item in raw.split():
        token = item.strip()
        if len(token) < 4 or token in _COMMON_LINK_TOKENS:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def _build_link_relevance_tokens(*, game_name: str, developer: str, package_id: str) -> set[str]:
    tokens: set[str] = set()
    for token in _tokenize_link_relevance(game_name):
        tokens.add(token)
    for token in _tokenize_link_relevance(developer):
        tokens.add(token)
    package_parts = [
        item
        for item in re.split(r"[^a-z0-9]+", str(package_id or "").lower())
        if item and len(item) >= 3 and item not in _COMMON_LINK_TOKENS
    ]
    for item in package_parts:
        if len(item) >= 4:
            tokens.add(item)
    for index in range(len(package_parts) - 1):
        combo = f"{package_parts[index]}{package_parts[index + 1]}"
        if len(combo) >= 6:
            tokens.add(combo)
    return tokens


def _link_matches_relevance(*, parsed, host: str, relevance_tokens: set[str]) -> bool:
    if not relevance_tokens:
        return True
    haystack = f"{host}{parsed.path or ''}{parsed.query or ''}".lower()
    for token in relevance_tokens:
        if token and token in haystack:
            return True
    return False


def _extract_social_links_from_html(
    raw_html: str,
    *,
    relevance_tokens: set[str] | None = None,
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen_hosts: set[str] = set()
    seen_urls: set[str] = set()
    seen_social_types: set[str] = set()
    tokens = set(relevance_tokens or set())
    for url in _extract_urls_from_html(raw_html):
        parsed = urlparse(url)
        host = parsed.netloc.lower().split(":")[0]
        if not host:
            continue
        if any(token in host for token in _SKIP_EXTERNAL_HOST_PARTS):
            continue
        if re.search(r"\.(png|jpe?g|gif|webp|svg|ico)$", parsed.path or "", flags=re.I):
            continue

        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query and len(parsed.query) <= 120:
            normalized_url += f"?{parsed.query}"
        if not normalized_url or normalized_url in seen_urls:
            continue

        link_type = "official"
        for token, mapped_type in _SOCIAL_DOMAIN_HINTS.items():
            if token in host:
                link_type = mapped_type
                break

        if tokens and not _link_matches_relevance(parsed=parsed, host=host, relevance_tokens=tokens):
            continue

        if link_type == "official":
            if host in seen_hosts:
                continue
            seen_hosts.add(host)
            label = f"Official Website ({host.replace('www.', '')})"
        else:
            if link_type in seen_social_types:
                continue
            seen_social_types.add(link_type)
            label = _SOCIAL_LABELS.get(link_type, link_type.upper())

        seen_urls.add(normalized_url)
        links.append({"type": link_type, "url": normalized_url, "label": label})
        if len(links) >= 8:
            break

    return links


def _extract_highlights(text: str, limit: int = 6) -> list[str]:
    raw = _sanitize_import_text(text)
    if not raw:
        return []
    pieces = re.split(r"[。！？!?；;\n\r]+", raw)
    highlights: list[str] = []
    for piece in pieces:
        p = piece.strip()
        if len(p) < 10:
            continue
        if _contains_long_token(p, min_len=70):
            continue
        highlights.append(p[:120])
        if len(highlights) >= limit:
            break
    return highlights


def _clean_overview_sentence(value: str) -> str:
    text = _clean_text_block(value)
    if not text:
        return ""
    text = re.sub(r"^[\[\(【（]?\s*(?:遊戲特色|游戏特色|features?)\s*[】）\)]?\s*", "", text, flags=re.I)
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.;:，。；：")
    return text


def _is_noisy_overview_sentence(value: str) -> bool:
    text = _clean_overview_sentence(value)
    if not text:
        return True
    lowered = text.lower()
    if "@" in text and "5v5" not in lowered:
        return True
    return any(hint in lowered for hint in _OVERVIEW_NOISE_HINTS)


def _extract_overview_sentences(text: str, *, limit: int = 4) -> list[str]:
    raw = _sanitize_import_text(text)
    if not raw:
        return []
    normalized = (
        raw.replace("【遊戲特色】", " ")
        .replace("【游戏特色】", " ")
        .replace("游戏特色", " ")
        .replace("遊戲特色", " ")
    )
    pieces = re.split(r"[。！？!?；;\n\r]+|(?=\s*\d+\.\s*)", normalized)
    rows: list[str] = []
    for piece in pieces:
        cleaned = _clean_overview_sentence(piece)
        if len(cleaned) < 12:
            continue
        if _contains_long_token(cleaned, min_len=70):
            continue
        if _is_noisy_overview_sentence(cleaned):
            continue
        if any(_similarity(cleaned, exists) >= 0.92 for exists in rows):
            continue
        rows.append(cleaned[:180])
        if len(rows) >= limit:
            break
    return rows


def _build_overview_html(detail_text: str, *, fallback_text: str) -> str:
    overview_lines = _extract_overview_sentences(detail_text, limit=4)
    if not overview_lines:
        overview_lines = _extract_overview_sentences(fallback_text, limit=3)
    if not overview_lines:
        fallback = _clean_overview_sentence(fallback_text)[:200]
        if fallback:
            overview_lines = [fallback]
    if not overview_lines:
        overview_lines = ["请先查看上方玩法亮点与官方链接，再根据区服和账号信息完成充值。"]
    return "".join(f"<p>{escape(line)}</p>" for line in overview_lines)


def _build_product_content_html(
    *,
    game_name: str,
    description: str,
    detail_text: str,
    google_play_url: str,
    social_links: list[dict[str, str]],
) -> str:
    safe_name = escape(_clean_text_block(game_name) or "Game")
    description_clean = _sanitize_import_text(description, fallback=detail_text)
    detail_plain = _sanitize_import_text(detail_text, fallback=description_clean)
    short_desc = escape((description_clean or detail_plain or _clean_text_block(game_name))[:600])
    highlights = _extract_highlights(detail_plain, limit=6)
    if not highlights:
        highlights = _extract_highlights(description_clean, limit=4)

    app_store_url = f"https://apps.apple.com/tw/iphone/search?term={quote(_clean_text_block(game_name) or 'game')}"

    links_html = [
        f'<li><a href="{escape(google_play_url, quote=True)}" target="_blank" rel="noopener noreferrer">Google Play 官方页</a></li>',
        f'<li><a href="{escape(app_store_url, quote=True)}" target="_blank" rel="noopener noreferrer">App Store 搜索</a></li>',
    ]
    for item in social_links[:8]:
        link_url = escape(str(item.get("url") or "").strip(), quote=True)
        if not link_url:
            continue
        link_type = escape(str(item.get("label") or item.get("type") or "官网").strip())
        links_html.append(
            f'<li><a href="{link_url}" target="_blank" rel="noopener noreferrer">{link_type}</a></li>'
        )

    if not highlights:
        highlights_html = "<li>充值前请确认区服、角色ID与账号信息，避免下单错误。</li>"
    else:
        highlights_html = "".join(f"<li>{escape(item)}</li>" for item in highlights)

    overview_html = _build_overview_html(
        detail_text=detail_plain or description_clean,
        fallback_text=description_clean or detail_plain,
    )
    return (
        '<article class="game-auto-import-content">'
        f"<h2>{safe_name}</h2>"
        f"<p>{short_desc}</p>"
        "<h3>玩法亮点</h3>"
        f"<ul>{highlights_html}</ul>"
        "<h3>官方与社交链接</h3>"
        f"<ul>{''.join(links_html)}</ul>"
        "<h3>游戏概览</h3>"
        f"{overview_html}"
        "</article>"
    )

def _resolve_topup_template(*, template_key: str) -> tuple[str, str, str]:
    from game_page.models import GamePageTemplate

    normalized_key = str(template_key or "default").strip().lower()[:50] or "default"
    template = GamePageTemplate.objects.filter(key=normalized_key).first()
    if template is None:
        template = GamePageTemplate.objects.order_by("key").first()
    if template is None:
        return "", "", ""

    topup_info = _normalize_topup_template_content(str(template.topup_info or ""))
    topup_info_tw = _normalize_topup_template_content(str(template.topup_info_tw or ""))
    if not topup_info and topup_info_tw:
        topup_info = topup_info_tw
    if not topup_info_tw and topup_info:
        topup_info_tw = topup_info

    return (
        topup_info,
        topup_info_tw,
        str(template.key or normalized_key),
    )


def _normalize_google_play_package_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    raw = raw.split("&", 1)[0].split("#", 1)[0].strip()
    if not raw or " " in raw:
        return ""
    if len(raw) < 6 or len(raw) > 180:
        return ""
    if raw.startswith(".") or raw.endswith(".") or ".." in raw:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9._]+", raw):
        return ""
    if "." not in raw:
        return ""
    return raw


def _build_daily_article_keywords(*, game_title: str, index: int) -> tuple[str, list[str]]:
    if not _DAILY_ARTICLE_TOPIC_PLAN:
        return "综合资讯", [game_title, "兑换码", "游戏攻略", "版本更新", "近期活动", "福利规划"]
    topic_title, topic_keywords = _DAILY_ARTICLE_TOPIC_PLAN[(max(1, index) - 1) % len(_DAILY_ARTICLE_TOPIC_PLAN)]
    base = [game_title, topic_title, "兑换码", "游戏攻略", "版本更新", "近期活动", "福利规划", "充值", "代储"]
    merged: list[str] = []
    seen: set[str] = set()
    for token in [*base, *(topic_keywords or [])]:
        value = str(token or "").strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(value)
    return topic_title, merged


def _extract_google_play_package_ids(raw_html: str) -> list[str]:
    normalized = (
        str(raw_html or "")
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("\\/", "/")
        .replace("&amp;", "&")
    )
    package_ids: list[str] = []
    seen: set[str] = set()
    for raw in _GOOGLE_PLAY_ID_RE.findall(normalized):
        value = _normalize_google_play_package_id(raw)
        if not value or value in seen:
            continue
        seen.add(value)
        package_ids.append(value)
    return package_ids


def discover_missing_google_play_package_ids(
    *,
    limit: int = 40,
    progress_callback: Callable[[str, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    from game_page.models import GamePage

    target = max(1, min(400, _safe_int(limit, default=40)))
    existing_ids = {
        str(item or "").strip()
        for item in GamePage.objects.exclude(google_play_id__exact="").values_list("google_play_id", flat=True)
        if str(item or "").strip()
    }

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    discovered: list[str] = []
    seen: set[str] = set()
    checked_seeds: list[dict[str, Any]] = []
    seed_total = len(_GOOGLE_PLAY_DISCOVERY_SEEDS)

    def _emit(stage: str, detail: dict[str, Any] | None = None) -> None:
        if not callable(progress_callback):
            return
        try:
            progress_callback(stage, detail or {})
        except Exception:
            pass

    _emit("started", {"target_count": target, "seed_total": seed_total})

    for seed_index, seed_url in enumerate(_GOOGLE_PLAY_DISCOVERY_SEEDS, start=1):
        if len(discovered) >= target:
            break
        row: dict[str, Any] = {"seed_url": seed_url, "status": "ok", "found": 0}
        _emit(
            "seed.started",
            {
                "index": seed_index,
                "total": seed_total,
                "seed_url": seed_url,
                "already_discovered": len(discovered),
            },
        )
        try:
            response = requests.get(
                seed_url,
                timeout=min(_REQUEST_TIMEOUT, 15),
                headers={
                    "User-Agent": user_agent,
                    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://play.google.com/",
                },
            )
        except Exception as exc:
            row["status"] = "request_error"
            row["error"] = str(exc)[:180]
            checked_seeds.append(row)
            _emit(
                "seed.completed",
                {
                    "index": seed_index,
                    "total": seed_total,
                    "status": row["status"],
                    "found": 0,
                    "discovered_count": len(discovered),
                    "error": row.get("error", ""),
                },
            )
            continue

        row["http_status"] = int(response.status_code or 0)
        if response.status_code != 200:
            row["status"] = "http_error"
            checked_seeds.append(row)
            _emit(
                "seed.completed",
                {
                    "index": seed_index,
                    "total": seed_total,
                    "status": row["status"],
                    "http_status": row["http_status"],
                    "found": 0,
                    "discovered_count": len(discovered),
                },
            )
            continue

        package_ids = _extract_google_play_package_ids(response.text or "")
        row["found"] = len(package_ids)
        for package_id in package_ids:
            if package_id in existing_ids or package_id in seen:
                continue
            seen.add(package_id)
            discovered.append(package_id)
            if len(discovered) >= target:
                break
        checked_seeds.append(row)
        _emit(
            "seed.completed",
            {
                "index": seed_index,
                "total": seed_total,
                "status": row["status"],
                "http_status": row.get("http_status"),
                "found": row["found"],
                "discovered_count": len(discovered),
            },
        )

    result = {
        "status": "completed" if discovered else "empty",
        "target_count": target,
        "discovered_count": len(discovered),
        "package_ids": discovered[:target],
        "checked_seeds": checked_seeds,
    }
    _emit(
        "finished",
        {
            "status": result["status"],
            "target_count": target,
            "discovered_count": len(discovered),
            "checked_seed_count": len(checked_seeds),
        },
    )
    return result


def run_google_play_import_automation(
    *,
    actor,
    play_urls: list[str] | None = None,
    package_ids: list[str] | None = None,
    template_key: str = "default",
    category_id: int | None = None,
    publish_status: str = "draft",
    overwrite_existing: bool = False,
    limit: int = 20,
    auto_discover_missing: bool = False,
    progress_callback: Callable[[str, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    from game_page.models import GamePage, GamePageCategory
    from game_page.scraper import GooglePlayScraper

    scraper = GooglePlayScraper()
    max_items = max(1, min(100, _safe_int(limit, default=20)))

    def _emit(stage: str, detail: dict[str, Any] | None = None) -> None:
        if not callable(progress_callback):
            return
        try:
            progress_callback(stage, detail or {})
        except Exception:
            pass

    candidates: list[str] = []
    for raw in play_urls or []:
        value = str(raw or "").strip()
        if not value:
            continue
        package_id = scraper.extract_id_from_url(value)
        if package_id:
            normalized = _normalize_google_play_package_id(package_id)
            if normalized:
                candidates.append(normalized)
    for raw in package_ids or []:
        value = str(raw or "").strip()
        normalized = _normalize_google_play_package_id(value)
        if normalized:
            candidates.append(normalized)

    discovery_result: dict[str, Any] = {}
    if not candidates and auto_discover_missing:
        discovery_result = discover_missing_google_play_package_ids(limit=max_items * 2)
        candidates.extend(discovery_result.get("package_ids") or [])

    if not candidates:
        fallback_rows = (
            GamePage.objects.exclude(google_play_id__exact="")
            .filter(Q(is_hot=True) | Q(is_recommended=True))
            .order_by("-updated_at")[:max_items]
        )
        candidates.extend(str(item.google_play_id or "").strip() for item in fallback_rows if item.google_play_id)

    deduped_candidates: list[str] = []
    seen_candidate: set[str] = set()
    for raw in candidates:
        value = str(raw or "").strip()
        if not value or value in seen_candidate:
            continue
        seen_candidate.add(value)
        deduped_candidates.append(value)
        if len(deduped_candidates) >= max_items:
            break
    _emit("candidates_ready", {"target_count": len(deduped_candidates), "limit": max_items})

    template_info, template_info_tw, template_used = _resolve_topup_template(template_key=template_key)
    chosen_category = GamePageCategory.objects.filter(pk=category_id).first() if category_id else None
    if chosen_category is None:
        chosen_category = GamePageCategory.objects.filter(is_active=True).order_by("sort_order", "id").first()

    items: list[dict[str, Any]] = []
    created_count = 0
    updated_count = 0
    failed_count = 0

    for index, package_id in enumerate(deduped_candidates, start=1):
        _emit(
            "item_started",
            {
                "index": index,
                "total": len(deduped_candidates),
                "package_id": package_id,
            },
        )
        play_url = f"https://play.google.com/store/apps/details?id={quote(package_id, safe='._-')}"
        data = scraper.fetch_game_info(play_url)
        if "error" in data:
            failed_count += 1
            items.append(
                {
                    "package_id": package_id,
                    "play_url": play_url,
                    "status": "failed",
                    "error": str(data.get("error") or "")[:300],
                }
            )
            _emit(
                "item_finished",
                {
                    "index": index,
                    "total": len(deduped_candidates),
                    "package_id": package_id,
                    "status": "failed",
                },
            )
            continue

        title = _clean_text_block(str(data.get("title") or ""))
        description = _sanitize_import_text(
            str(data.get("description") or ""),
            fallback=str(data.get("content") or ""),
        )
        detail_text = _sanitize_import_text(
            str(data.get("content") or ""),
            fallback=description,
        )
        developer = _clean_text_block(str(data.get("developer") or ""))
        icon_url = str(data.get("icon_url") or "").strip()

        social_links: list[dict[str, str]] = []
        relevance_tokens = _build_link_relevance_tokens(
            game_name=title or package_id,
            developer=developer,
            package_id=package_id,
        )
        try:
            page_resp = requests.get(
                play_url,
                headers=getattr(scraper, "HEADERS", {}) or {"User-Agent": "Mozilla/5.0"},
                timeout=getattr(scraper, "REQUEST_TIMEOUT", _REQUEST_TIMEOUT),
            )
            if page_resp.status_code == 200:
                social_links = _extract_social_links_from_html(
                    page_resp.text,
                    relevance_tokens=relevance_tokens,
                )
        except Exception:
            social_links = []

        content_html = _build_product_content_html(
            game_name=title or package_id,
            description=description,
            detail_text=detail_text or description,
            google_play_url=play_url,
            social_links=social_links,
        )

        game_page = GamePage.objects.filter(google_play_id=package_id).first()
        if game_page is None and title:
            game_page = GamePage.objects.filter(title__iexact=title).order_by("-updated_at").first()

        is_created = game_page is None
        if game_page is None:
            game_page = GamePage(
                google_play_id=package_id,
                author=actor if getattr(actor, "is_authenticated", False) else None,
            )

        def _assign(field: str, value: Any, *, force: bool = False) -> None:
            if value is None:
                return
            current = getattr(game_page, field, "")
            if force or overwrite_existing or not current:
                setattr(game_page, field, value)

        title_text = title or package_id
        description_text = description or detail_text or title_text
        platform_text = "Android / iOS"
        regions_text = "Global / 港台服"

        title_i18n_map = _build_import_i18n_map(
            default_text=title_text,
            tw_text=title_text,
            existing_map=getattr(game_page, "title_i18n", {}),
        )
        description_i18n_map = _build_import_i18n_map(
            default_text=description_text,
            tw_text=description_text,
            existing_map=getattr(game_page, "description_i18n", {}),
        )
        content_i18n_map = _build_import_i18n_map(
            default_text=content_html,
            tw_text=content_html,
            existing_map=getattr(game_page, "content_i18n", {}),
        )
        platform_i18n_map = _build_import_i18n_map(
            default_text=platform_text,
            tw_text=platform_text,
            existing_map=getattr(game_page, "platform_i18n", {}),
        )
        regions_i18n_map = _build_import_i18n_map(
            default_text=regions_text,
            tw_text=regions_text,
            existing_map=getattr(game_page, "regions_i18n", {}),
        )

        _assign("title", title_text)
        _assign("title_tw", title_text)
        _assign("title_i18n", title_i18n_map, force=True)
        _assign("developer", developer)
        _assign("google_play_id", package_id, force=True)
        _assign("description", description_text, force=True)
        _assign("description_tw", description_text, force=True)
        _assign("description_i18n", description_i18n_map, force=True)
        _assign("content", content_html, force=True)
        _assign("content_tw", content_html, force=True)
        _assign("content_i18n", content_i18n_map, force=True)
        _assign("icon_external_url", icon_url)
        _assign("platform", platform_text)
        _assign("platform_i18n", platform_i18n_map, force=True)
        _assign("regions", regions_text)
        _assign("regions_i18n", regions_i18n_map, force=True)
        _assign("seo_title", f"{title or package_id} 充值与攻略")
        _assign("seo_keywords", ",".join([title or package_id, "充值", "代储", "攻略"]))
        _assign("seo_description", (description or detail_text or f"{title or package_id} 游戏介绍")[:200])
        if template_info:
            _assign("topup_info", template_info, force=True)
        if template_info_tw:
            _assign("topup_info_tw", template_info_tw, force=True)
        elif template_info:
            _assign("topup_info_tw", template_info, force=True)
        if template_info or template_info_tw:
            topup_i18n_map = _build_import_i18n_map(
                default_text=template_info or template_info_tw,
                tw_text=template_info_tw or template_info,
                existing_map=getattr(game_page, "topup_info_i18n", {}),
            )
            _assign(
                "topup_info_i18n",
                topup_i18n_map,
                force=True,
            )
        if chosen_category and game_page.category_id is None:
            game_page.category = chosen_category

        if publish_status == "published":
            game_page.status = "published"
            if not game_page.published_at:
                game_page.published_at = timezone.now()
        elif game_page.status not in {"draft", "published", "archived"}:
            game_page.status = "draft"

        game_page.save()

        if icon_url and (overwrite_existing or not game_page.icon_image):
            try:
                media = scraper.save_icon_to_media_library(
                    icon_url,
                    title or package_id,
                    package_id=package_id,
                )
                if media and getattr(media, "file", None):
                    game_page.icon_image = media.file
                    game_page.save(update_fields=["icon_image", "updated_at"])
            except Exception:
                pass

        if is_created:
            created_count += 1
            row_status = "created"
        else:
            updated_count += 1
            row_status = "updated"

        items.append(
            {
                "package_id": package_id,
                "play_url": play_url,
                "status": row_status,
                "game_page_id": game_page.id,
                "title": game_page.title,
                "social_links_count": len(social_links),
                "template_key": template_used,
            }
        )
        _emit(
            "item_finished",
            {
                "index": index,
                "total": len(deduped_candidates),
                "package_id": package_id,
                "status": row_status,
            },
        )

    _emit(
        "completed",
        {
            "status": "completed" if failed_count == 0 else ("partial" if items else "failed"),
            "target_count": len(deduped_candidates),
            "created_count": created_count,
            "updated_count": updated_count,
            "failed_count": failed_count,
        },
    )
    return {
        "status": "completed" if failed_count == 0 else ("partial" if items else "failed"),
        "target_count": len(deduped_candidates),
        "created_count": created_count,
        "updated_count": updated_count,
        "failed_count": failed_count,
        "template_key": template_used,
        "discovery": discovery_result,
        "items": items,
    }


def discover_bahamut_bsn_for_game(game) -> dict[str, Any]:
    title = str(getattr(game, "title", "") or "").strip()
    if not title:
        return {"bsn": None, "board_url": "", "source": "ranking_empty_title", "confidence": 0.0}

    if not callable(resolve_bahamut_bsn_for_game_title):
        return {"bsn": None, "board_url": "", "source": "ranking_module_unavailable", "confidence": 0.0}

    ranked = resolve_bahamut_bsn_for_game_title(title)
    if not isinstance(ranked, dict):
        return {"bsn": None, "board_url": "", "source": "ranking_invalid_result", "confidence": 0.0}

    bsn = _safe_int(ranked.get("bsn"), default=0)
    board_url = str(ranked.get("board_url") or "").strip()
    try:
        confidence = float(ranked.get("confidence") or 0.0)
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    source = str(ranked.get("source") or "bahamut_ranking_cache")

    if bsn <= 0:
        return {
            "bsn": None,
            "board_url": "",
            "source": source or "ranking_no_match",
            "confidence": round(confidence, 3),
        }

    normalized = dict(ranked)
    normalized["bsn"] = int(bsn)
    normalized["board_url"] = board_url or f"https://forum.gamer.com.tw/B.php?bsn={int(bsn)}"
    normalized["source"] = source
    normalized["confidence"] = round(confidence, 3)
    return normalized


def _find_duplicate_articles(seo_article, *, candidate_title: str, candidate_body: str) -> list[dict[str, Any]]:
    from game_article.models import Article

    title_norm = _normalize_for_similarity(candidate_title)
    body_norm = _normalize_for_similarity(candidate_body)[:2600]

    queryset = Article.objects.filter(status="published")
    if getattr(seo_article, "published_article_id", None):
        queryset = queryset.exclude(pk=seo_article.published_article_id)
    if getattr(seo_article, "game_id", None):
        queryset = queryset.filter(Q(game_id=seo_article.game_id) | Q(title__icontains=seo_article.game.title))
    queryset = queryset.order_by("-published_at", "-id")[:120]

    duplicates: list[dict[str, Any]] = []
    for article in queryset:
        other_title_norm = _normalize_for_similarity(str(article.title or ""))
        other_body_norm = _normalize_for_similarity(str(article.content or ""))[:2600]
        title_ratio = _similarity(title_norm, other_title_norm)
        body_ratio = _similarity(body_norm, other_body_norm)
        if title_ratio >= 0.88 or body_ratio >= 0.92:
            duplicates.append(
                {
                    "article_id": article.id,
                    "title": article.title,
                    "title_ratio": round(title_ratio, 4),
                    "body_ratio": round(body_ratio, 4),
                    "similarity": round(max(title_ratio, body_ratio), 4),
                    "engagement": _engagement_score(article),
                }
            )
    duplicates.sort(key=lambda item: (item["similarity"], item["engagement"]), reverse=True)
    return duplicates


def evaluate_robot_quality_for_seo_article(seo_article, *, threshold: int = 72) -> dict[str, Any]:
    body_html = str(getattr(seo_article, "body_html", "") or "")
    plain_text = _strip_html(body_html)
    content_len = len(plain_text)
    h2_count = len(re.findall(r"<h2\b", body_html, flags=re.I))
    h3_count = len(re.findall(r"<h3\b", body_html, flags=re.I))
    img_count = len(re.findall(r"<img\b", body_html, flags=re.I))
    dynamic_img_hits = len(re.findall(r"<img[^>]+(?:\.gif|\.webp|image/gif|format=gif)", body_html, flags=re.I))
    tags = getattr(seo_article, "tags", []) or []

    rewrite_payload = getattr(seo_article, "rewrite_payload", {})
    if not isinstance(rewrite_payload, dict):
        rewrite_payload = {}
    step5_quality = rewrite_payload.get("step5_quality")
    if not isinstance(step5_quality, dict):
        step5_quality = {}
    selected_images = step5_quality.get("selected_images")
    if not isinstance(selected_images, list):
        selected_images = []
    selected_scores: list[float] = []
    selected_relevance_scores: list[float] = []
    selected_quality_scores: list[float] = []
    strict_quality_pass_count = 0
    watermark_safe_count = 0
    for item in selected_images:
        if not isinstance(item, dict):
            continue
        score_value = item.get("score", item.get("quality_score"))
        relevance_value = item.get("relevance_score")
        quality_value = item.get("quality_score")
        try:
            selected_scores.append(float(score_value))
        except Exception:
            pass
        try:
            selected_relevance_scores.append(float(relevance_value))
        except Exception:
            pass
        try:
            selected_quality_scores.append(float(quality_value))
        except Exception:
            pass
        if bool(item.get("strict_quality_pass", False)):
            strict_quality_pass_count += 1
        if bool(item.get("watermark_safe", False)):
            watermark_safe_count += 1
    best_image_score = max(selected_scores) if selected_scores else 0.0
    avg_image_score = (sum(selected_scores) / len(selected_scores)) if selected_scores else 0.0
    avg_relevance_score = (
        (sum(selected_relevance_scores) / len(selected_relevance_scores)) if selected_relevance_scores else 0.0
    )
    avg_quality_score = (
        (sum(selected_quality_scores) / len(selected_quality_scores)) if selected_quality_scores else 0.0
    )
    validation_diag = step5_quality.get("validation")
    if not isinstance(validation_diag, dict):
        validation_diag = {}
    rejected_dynamic = _safe_int(validation_diag.get("rejected_dynamic"), 0)
    rejected_low_quality = _safe_int(validation_diag.get("rejected_low_quality"), 0)
    rejected_text_or_watermark = _safe_int(validation_diag.get("rejected_text_or_watermark"), 0)
    published_article = getattr(seo_article, "published_article", None)
    has_cover_image = bool(getattr(published_article, "cover_image", None))

    score = 100
    issues: list[str] = []
    if content_len < 1000:
        score -= 28
        issues.append("正文长度偏短（<1000）")
    elif content_len < 1500:
        score -= 12
        issues.append("正文长度一般（<1500）")
    if h2_count < 3:
        score -= 10
        issues.append("H2 小节不足")
    if h3_count < 2:
        score -= 6
        issues.append("H3 小节不足")
    if img_count < 2:
        score -= 8
        issues.append("配图不足")
    if dynamic_img_hits > 0:
        score -= 16
        issues.append("检测到动态图片或不稳定图片格式")
    if not selected_images:
        score -= 20
        issues.append("未命中高质量静态配图")
    elif len(selected_images) < 2:
        score -= 14
        issues.append("高质量配图数量不足（<2）")
    elif avg_image_score < 0.66:
        score -= 16
        issues.append("配图综合评分偏低")
    if best_image_score < 0.72:
        score -= 8
        issues.append("配图最高分不足")
    if avg_relevance_score < 0.34:
        score -= 10
        issues.append("配图相关度不足")
    if avg_quality_score < 0.64:
        score -= 10
        issues.append("配图清晰度不足")
    if watermark_safe_count < len(selected_images):
        score -= 14
        issues.append("配图存在潜在水印风险")
    if strict_quality_pass_count < len(selected_images):
        score -= 8
        issues.append("存在未通过严格质检的配图")
    if len(tags) < 4:
        score -= 6
        issues.append("关键词覆盖偏少")
    if not str(getattr(seo_article, "meta_title", "") or "").strip():
        score -= 8
        issues.append("Meta title 缺失")
    if not str(getattr(seo_article, "meta_description", "") or "").strip():
        score -= 10
        issues.append("Meta description 缺失")
    if published_article is not None and not has_cover_image:
        score -= 16
        issues.append("已发布文章缺少封面图")

    garbled_hits = plain_text.count("\uFFFD") + len(re.findall(r"\?{3,}", plain_text))
    if garbled_hits > 0:
        score -= 25
        issues.append("检测到潜在乱码")

    duplicates = _find_duplicate_articles(
        seo_article,
        candidate_title=str(getattr(seo_article, "title", "") or ""),
        candidate_body=plain_text,
    )
    keep_existing_duplicate = False
    if duplicates:
        score -= 30
        issues.append("疑似重复主题")
        best_duplicate = max(duplicates, key=lambda item: item["engagement"])
        keep_existing_duplicate = best_duplicate["engagement"] > 0

    score = max(0, min(100, score))
    expected_threshold = max(1, min(100, _safe_int(threshold, default=72)))
    strict_image_policy_pass = (
        len(selected_images) >= 2
        and img_count >= 2
        and dynamic_img_hits == 0
        and best_image_score >= 0.72
        and avg_image_score >= 0.66
        and avg_relevance_score >= 0.34
        and avg_quality_score >= 0.64
        and strict_quality_pass_count >= len(selected_images)
        and watermark_safe_count >= len(selected_images)
    )
    if not strict_image_policy_pass and "资讯配图未达到严格无水印高质量标准" not in issues:
        issues.append("资讯配图未达到严格无水印高质量标准")

    return {
        "score": score,
        "threshold": expected_threshold,
        "pass": score >= expected_threshold and not keep_existing_duplicate and strict_image_policy_pass,
        "issues": issues,
        "metrics": {
            "content_len": content_len,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "img_count": img_count,
            "dynamic_img_hits": dynamic_img_hits,
            "tag_count": len(tags),
            "garbled_hits": garbled_hits,
            "selected_image_count": len(selected_images),
            "best_image_score": round(best_image_score, 4),
            "avg_image_score": round(avg_image_score, 4),
            "avg_relevance_score": round(avg_relevance_score, 4),
            "avg_quality_score": round(avg_quality_score, 4),
            "strict_quality_pass_count": strict_quality_pass_count,
            "watermark_safe_count": watermark_safe_count,
            "rejected_dynamic": rejected_dynamic,
            "rejected_low_quality": rejected_low_quality,
            "rejected_text_or_watermark": rejected_text_or_watermark,
            "has_cover_image": has_cover_image,
            "strict_image_policy_pass": strict_image_policy_pass,
        },
        "duplicates": duplicates[:8],
        "keep_existing_duplicate": keep_existing_duplicate,
    }


def _needs_additional_bahamut_crawl(review: dict[str, Any]) -> bool:
    if not isinstance(review, dict):
        return False
    if bool(review.get("pass")):
        return False
    if bool(review.get("keep_existing_duplicate")):
        return False

    metrics = review.get("metrics")
    if not isinstance(metrics, dict):
        metrics = {}

    content_len = _safe_int(metrics.get("content_len"), default=0)
    h2_count = _safe_int(metrics.get("h2_count"), default=0)
    h3_count = _safe_int(metrics.get("h3_count"), default=0)
    img_count = _safe_int(metrics.get("img_count"), default=0)
    selected_image_count = _safe_int(metrics.get("selected_image_count"), default=0)
    garbled_hits = _safe_int(metrics.get("garbled_hits"), default=0)
    strict_image_policy_pass = bool(metrics.get("strict_image_policy_pass", False))
    try:
        avg_image_score = float(metrics.get("avg_image_score") or 0.0)
    except Exception:
        avg_image_score = 0.0

    score = _safe_int(review.get("score"), default=0)
    threshold = _safe_int(review.get("threshold"), default=72)
    issues_text = " ".join(str(item or "") for item in (review.get("issues") or []))
    has_precision_issue = any(
        token in issues_text
        for token in (
            "正文长度",
            "H2",
            "H3",
            "配图不足",
            "乱码",
            "高质量静态配图",
            "配图综合评分偏低",
            "资讯配图未达到严格无水印高质量标准",
        )
    )

    if content_len < 1400 or h2_count < 3 or h3_count < 2:
        return True
    if img_count < 2 or selected_image_count < 2 or avg_image_score < 0.66:
        return True
    if not strict_image_policy_pass:
        return True
    if garbled_hits > 0:
        return True
    if has_precision_issue:
        return True
    if score < max(1, threshold - 10):
        return True
    return False


def _archive_article_if_exists(article_id: int | None, *, reason: str) -> bool:
    if not article_id:
        return False
    from game_article.models import Article

    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return False
    article.status = "archived"
    summary = str(article.summary or "")
    reason_text = f"[AUTO_ARCHIVE] {reason}".strip()
    if reason_text not in summary:
        article.summary = (summary + "\n" + reason_text).strip()[:500]
    article.save(update_fields=["status", "summary", "updated_at"])
    return True


def rewrite_low_quality_seo_article(*, seo_article, actor=None, reason: str = "") -> dict[str, Any]:
    from seo_automation.services import (
        build_meta_fields,
        build_standalone_seo_html_document,
        compose_rich_seo_article_html,
        inject_game_internal_link,
        merge_unique_tags,
        rewrite_bahamut_text,
    )
    from seo_automation.views import _refresh_seo_article_source_and_media

    game_name = (
        seo_article.game.title
        if getattr(seo_article, "game", None)
        else str(getattr(seo_article, "title", "") or "娓告垙")
    )
    raw_text = str(getattr(seo_article, "raw_text", "") or "").strip()
    if not raw_text:
        raw_text = _strip_html(str(getattr(seo_article, "body_html", "") or ""))[:5000]

    rewrite = rewrite_bahamut_text(
        raw_text=raw_text,
        game_name=game_name,
        keywords=list(getattr(seo_article, "tags", []) or []),
    )
    merged_tags = merge_unique_tags(
        base_tags=list(rewrite.get("tags") or []),
        extra_tags=list(getattr(seo_article, "tags", []) or []),
        limit=12,
    )
    body_html = compose_rich_seo_article_html(
        title=str(rewrite.get("title") or seo_article.title),
        body_html=str(rewrite.get("body_html") or seo_article.body_html),
        game_name=game_name,
        summary=str(rewrite.get("meta_description") or seo_article.meta_description or ""),
        keywords=merged_tags,
        search_intent="informational",
        source_title=str(getattr(seo_article, "source_title", "") or seo_article.title),
        source_url=str(getattr(seo_article, "source_url", "") or ""),
        media_gallery_html="",
        media_items=[],
        generated_at=timezone.now(),
    )
    body_html = inject_game_internal_link(
        body_html=body_html,
        game_id=seo_article.game_id if getattr(seo_article, "game_id", None) else None,
        game_title=game_name,
        google_play_id=str(getattr(seo_article.game, "google_play_id", "") or "") if getattr(seo_article, "game", None) else "",
    )
    meta = build_meta_fields(
        title=str(rewrite.get("title") or seo_article.title),
        body_html=body_html,
        default_title=game_name,
    )
    standalone_html = build_standalone_seo_html_document(
        title=str(rewrite.get("title") or seo_article.title),
        meta_description=str(meta.get("meta_description") or ""),
        meta_keywords=",".join(merged_tags[:10]),
        body_html=body_html,
    )

    payload = dict(seo_article.rewrite_payload) if isinstance(seo_article.rewrite_payload, dict) else {}
    payload["title"] = str(rewrite.get("title") or seo_article.title)
    payload["body_html"] = body_html
    payload["final_body_html"] = body_html
    payload["meta_title"] = str(meta.get("meta_title") or "")
    payload["meta_description"] = str(meta.get("meta_description") or "")
    payload["tags"] = merged_tags
    payload["standalone_html"] = standalone_html
    payload["robot_rewrite"] = {
        "reason": reason or "quality_rewrite",
        "at": timezone.now().isoformat(),
        "model": ((rewrite.get("diagnostics") or {}).get("model") if isinstance(rewrite, dict) else "") or "",
    }

    seo_article.title = payload["title"][:220]
    seo_article.body_html = body_html
    seo_article.meta_title = payload["meta_title"][:120]
    seo_article.meta_description = payload["meta_description"][:220]
    seo_article.tags = merged_tags
    seo_article.rewrite_payload = payload
    seo_article.status = "review"
    seo_article.save(
        update_fields=[
            "title",
            "body_html",
            "meta_title",
            "meta_description",
            "tags",
            "rewrite_payload",
            "status",
            "updated_at",
        ]
    )

    quality_refresh = _refresh_seo_article_source_and_media(
        seo_article=seo_article,
        task_keyword=seo_article.task.keyword if getattr(seo_article, "task", None) else "",
        request_user=actor,
    )
    seo_article.refresh_from_db()
    return {
        "seo_article_id": seo_article.id,
        "status": "rewritten",
        "quality_refresh": quality_refresh,
    }


def _run_single_daily_seo_game(
    *,
    actor,
    game,
    index: int,
    post_min: int,
    post_max: int,
    crawl_attempt_limit: int,
    rewrite_limit_value: int,
    threshold: int,
    publish_now_flag: bool,
    rewrite_low_quality: bool,
    rank_pool_bsn_info: dict[str, Any] | None = None,
    enforce_rank_pool_bsn: bool = False,
) -> dict[str, Any]:
    from django.db import close_old_connections

    from seo_automation.models import CrawlerTask, SeoArticle
    from seo_automation.views import _publish_seo_article, _run_bahamut_pipeline

    close_old_connections()
    created_tasks = 0
    published_count = 0
    draft_count = 0
    failed_count = 0
    skipped_count = 0

    game_result: dict[str, Any] = {
        "game_id": game.id,
        "game_title": game.title,
        "status": "pending",
    }

    try:
        rank_pool_info = rank_pool_bsn_info if isinstance(rank_pool_bsn_info, dict) else {}
        rank_pool_bsn = _safe_int(rank_pool_info.get("bsn"), default=0)
        rank_pool_board_url = str(rank_pool_info.get("board_url") or "").strip()
        rank_pool_board_title = str(rank_pool_info.get("board_title") or "").strip()
        if rank_pool_bsn > 0:
            bsn_result = {
                "bsn": int(rank_pool_bsn),
                "board_url": rank_pool_board_url or f"https://forum.gamer.com.tw/B.php?bsn={int(rank_pool_bsn)}",
                "source": str(rank_pool_info.get("source") or "bahamut_rank_pool_selected"),
                "confidence": 1.0,
            }
            rank_pool_rank = _safe_int(rank_pool_info.get("rank"), default=0)
            rank_pool_rank_change = _safe_int(rank_pool_info.get("rank_change"), default=0)
            if rank_pool_board_title:
                game_result["rank_pool_board_title"] = rank_pool_board_title
            if rank_pool_rank > 0:
                game_result["rank_pool_rank"] = rank_pool_rank
            if rank_pool_rank_change:
                game_result["rank_pool_rank_change"] = rank_pool_rank_change
        elif enforce_rank_pool_bsn:
            bsn_result = {
                "bsn": None,
                "board_url": "",
                "source": "rank_pool_missing_bsn",
                "confidence": 0.0,
            }
        else:
            bsn_result = discover_bahamut_bsn_for_game(game)
        game_result["bsn"] = bsn_result.get("bsn")
        game_result["bsn_source"] = bsn_result.get("source")
        if not bsn_result.get("bsn"):
            skipped_count += 1
            game_result["status"] = "skipped_no_bsn"
            if enforce_rank_pool_bsn:
                game_result["error"] = "Selected game has no usable bsn in ranking pool."
            else:
                game_result["error"] = "Unable to discover bsn for this game."
            return {
                "index": index,
                "created_tasks": created_tasks,
                "published_count": published_count,
                "draft_count": draft_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "item": game_result,
            }

        board_url = str(bsn_result.get("board_url") or "").strip()
        if not board_url and _safe_int(bsn_result.get("bsn"), default=0) > 0:
            board_url = f"https://forum.gamer.com.tw/B.php?bsn={_safe_int(bsn_result.get('bsn'), default=0)}"
        if not board_url:
            skipped_count += 1
            game_result["status"] = "skipped_no_board_url"
            game_result["error"] = "Ranking pool did not return board_url."
            return {
                "index": index,
                "created_tasks": created_tasks,
                "published_count": published_count,
                "draft_count": draft_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "item": game_result,
            }

        base_max_posts = random.randint(post_min, post_max)
        topic_title, topic_keywords = _build_daily_article_keywords(
            game_title=str(game.title or ""),
            index=index,
        )
        max_crawl_attempts = crawl_attempt_limit
        crawl_attempts: list[dict[str, Any]] = []
        final_task_id = 0
        final_article_ids: list[int] = []
        review: dict[str, Any] = {}
        seo_article = None

        for crawl_attempt in range(1, max_crawl_attempts + 1):
            attempt_end_page = min(12, 2 + (crawl_attempt - 1) * 2)
            attempt_max_posts = min(120, base_max_posts + (crawl_attempt - 1) * 8)
            payload = {
                "source_url": board_url,
                "keyword": str(game.title or "").strip(),
                "start_page": 1,
                "end_page": attempt_end_page,
                "max_posts": attempt_max_posts,
                "stop_after_step": 5,
                "run_rewrite": True,
                "rewrite_limit": rewrite_limit_value,
                "store_draft": True,
                "auto_publish": False,
                "publish_now": False,
                "related_game_id": game.id,
                "custom_keywords": topic_keywords,
            }

            task = CrawlerTask.objects.create(
                name=f"Auto Daily SEO {game.title} - {topic_title} A{crawl_attempt}"[:200],
                source_platform="bahamut",
                source_url=payload["source_url"],
                keyword=payload["keyword"][:120],
                status="pending",
                progress=0,
                triggered_by=actor if getattr(actor, "is_authenticated", False) else None,
                request_payload=payload,
            )
            created_tasks += 1

            attempt_result: dict[str, Any] = {
                "attempt": crawl_attempt,
                "task_id": task.id,
                "end_page": attempt_end_page,
                "max_posts": attempt_max_posts,
            }
            try:
                pipeline_result = _run_bahamut_pipeline(task=task, payload=payload, request_user=actor)
            except Exception as exc:
                attempt_result["status"] = "failed_pipeline"
                attempt_result["error"] = str(exc)[:300]
                crawl_attempts.append(attempt_result)
                continue

            article_ids = [int(x) for x in (pipeline_result.get("article_ids") or []) if _safe_int(x) > 0]
            attempt_result["article_ids"] = article_ids
            if not article_ids:
                attempt_result["status"] = "failed_no_article"
                attempt_result["error"] = "Pipeline completed without generated article."
                crawl_attempts.append(attempt_result)
                continue

            candidate = (
                SeoArticle.objects.select_related("game", "task", "published_article")
                .filter(pk=article_ids[0])
                .first()
            )
            if not candidate:
                attempt_result["status"] = "failed_article_not_found"
                crawl_attempts.append(attempt_result)
                continue

            current_review = evaluate_robot_quality_for_seo_article(candidate, threshold=threshold)
            attempt_result["review"] = current_review

            if not current_review.get("pass") and rewrite_low_quality:
                try:
                    rewrite_info = rewrite_low_quality_seo_article(
                        seo_article=candidate,
                        actor=actor,
                        reason="daily_auto_quality_gate",
                    )
                    candidate.refresh_from_db()
                    current_review = evaluate_robot_quality_for_seo_article(candidate, threshold=threshold)
                    attempt_result["rewrite"] = rewrite_info
                    attempt_result["review_after_rewrite"] = current_review
                except Exception as exc:
                    current_review["pass"] = False
                    current_review.setdefault("issues", []).append(f"rewrite_failed: {str(exc)[:120]}")
                    attempt_result["review_after_rewrite"] = current_review

            attempt_result["final_pass"] = bool(current_review.get("pass"))
            seo_article = candidate
            review = current_review
            final_task_id = task.id
            final_article_ids = article_ids
            crawl_attempts.append(attempt_result)

            if crawl_attempt < max_crawl_attempts and _needs_additional_bahamut_crawl(current_review):
                attempt_result["status"] = "retry_deeper_crawl"
                continue

            attempt_result["status"] = "completed"
            break

        game_result["task_id"] = final_task_id
        game_result["article_ids"] = final_article_ids
        game_result["topic"] = topic_title
        game_result["crawl_attempts"] = crawl_attempts
        if crawl_attempts:
            last_attempt = crawl_attempts[-1]
            if isinstance(last_attempt, dict):
                if isinstance(last_attempt.get("review"), dict):
                    game_result["review"] = last_attempt["review"]
                if isinstance(last_attempt.get("review_after_rewrite"), dict):
                    game_result["review_after_rewrite"] = last_attempt["review_after_rewrite"]
                if isinstance(last_attempt.get("rewrite"), dict):
                    game_result["rewrite"] = last_attempt["rewrite"]

        if not seo_article:
            failed_count += 1
            game_result["status"] = "failed_no_article"
            game_result["error"] = (
                str(crawl_attempts[-1].get("error") or "Pipeline completed without generated article.")[:300]
                if crawl_attempts
                else "Pipeline completed without generated article."
            )
            return {
                "index": index,
                "created_tasks": created_tasks,
                "published_count": published_count,
                "draft_count": draft_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "item": game_result,
            }

        if not review.get("pass"):
            skipped_count += 1
            seo_article.status = "review"
            seo_article.save(update_fields=["status", "updated_at"])
            game_result["status"] = "kept_for_manual_review"
            return {
                "index": index,
                "created_tasks": created_tasks,
                "published_count": published_count,
                "draft_count": draft_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "item": game_result,
            }

        if review.get("keep_existing_duplicate"):
            skipped_count += 1
            seo_article.status = "review"
            seo_article.save(update_fields=["status", "updated_at"])
            game_result["status"] = "skipped_duplicate_keep_existing"
            game_result["duplicates"] = review.get("duplicates", [])
            return {
                "index": index,
                "created_tasks": created_tasks,
                "published_count": published_count,
                "draft_count": draft_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "item": game_result,
            }

        if review.get("duplicates"):
            for dup in review["duplicates"]:
                if _safe_int(dup.get("engagement"), 0) <= 0:
                    _archive_article_if_exists(
                        _safe_int(dup.get("article_id"), 0),
                        reason="daily_auto_duplicate_replace",
                    )

        published = _publish_seo_article(
            seo_article=seo_article,
            request_user=actor,
            publish_now=publish_now_flag,
            publish_at=None,
        )
        game_result["article_id"] = published.id
        if publish_now_flag:
            published_count += 1
            game_result["status"] = "published"
            game_result["published_article_id"] = published.id
        else:
            draft_count += 1
            game_result["status"] = "draft_saved"
            game_result["draft_article_id"] = published.id

        return {
            "index": index,
            "created_tasks": created_tasks,
            "published_count": published_count,
            "draft_count": draft_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "item": game_result,
        }
    except Exception as exc:
        failed_count += 1
        game_result["status"] = "failed_exception"
        game_result["error"] = str(exc)[:300]
        return {
            "index": index,
            "created_tasks": created_tasks,
            "published_count": published_count,
            "draft_count": draft_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "item": game_result,
        }
    finally:
        close_old_connections()


def run_seo_daily_automation(
    *,
    actor,
    game_ids: list[int] | None = None,
    limit_games: int = 6,
    posts_min: int = 10,
    posts_max: int = 20,
    max_attempts_per_game: int = 1,
    rewrite_limit: int = 1,
    publish_status: str = "published",
    publish_now: bool = True,
    rewrite_low_quality: bool = True,
    review_threshold: int = 72,
    recent_days: int = 30,
    pre_import_missing_games: bool = True,
    pre_import_limit: int = 30,
    post_recheck_published: bool = True,
    recheck_limit: int = 120,
    parallel_workers: int = 0,
    rank_pool_bsn_map: dict[int | str, dict[str, Any]] | None = None,
    enforce_rank_pool_bsn: bool = False,
) -> dict[str, Any]:
    from datetime import timedelta

    from game_page.models import GamePage

    threshold = max(1, min(100, _safe_int(review_threshold, default=72)))
    raw_limit_games = _safe_int(limit_games, default=6)
    max_games = max(1, min(100, raw_limit_games)) if raw_limit_games > 0 else 100
    apply_selected_game_limit = raw_limit_games > 0
    post_min = max(1, min(200, _safe_int(posts_min, default=10)))
    post_max = max(post_min, min(200, _safe_int(posts_max, default=20)))
    crawl_attempt_limit = max(1, min(5, _safe_int(max_attempts_per_game, default=1)))
    rewrite_limit_value = max(1, min(5, _safe_int(rewrite_limit, default=1)))
    normalized_publish_status = _normalize_publish_status(
        publish_status,
        fallback_publish_now=bool(publish_now),
    )
    publish_now_flag = normalized_publish_status == "published"
    recent_cutoff = timezone.now() - timedelta(days=max(1, _safe_int(recent_days, default=30)))

    pre_import: dict[str, Any] = {}
    auto_game_ids: list[int] = []
    if not game_ids and pre_import_missing_games:
        try:
            pre_import = run_google_play_import_automation(
                actor=actor,
                play_urls=[],
                package_ids=[],
                template_key="default",
                category_id=None,
                publish_status="draft",
                overwrite_existing=False,
                limit=max(1, min(100, _safe_int(pre_import_limit, default=30))),
                auto_discover_missing=True,
            )
            for row in pre_import.get("items") or []:
                status = str(row.get("status") or "").strip().lower()
                if status not in {"created", "updated"}:
                    continue
                game_id = _safe_int(row.get("game_page_id"), default=0)
                if game_id > 0:
                    auto_game_ids.append(game_id)
        except Exception as exc:
            pre_import = {"status": "failed", "error": str(exc)[:260]}

    selected_game_ids = game_ids or auto_game_ids
    if selected_game_ids:
        normalized_selected_ids: list[int] = []
        selected_seen: set[int] = set()
        for raw in selected_game_ids:
            game_id = _safe_int(raw, default=0)
            if game_id <= 0 or game_id in selected_seen:
                continue
            selected_seen.add(game_id)
            normalized_selected_ids.append(game_id)
        if apply_selected_game_limit:
            normalized_selected_ids = normalized_selected_ids[:max_games]

        if normalized_selected_ids:
            preserved_order = Case(
                *[When(pk=pk, then=idx) for idx, pk in enumerate(normalized_selected_ids)],
                default=len(normalized_selected_ids),
                output_field=IntegerField(),
            )
            games = list(
                GamePage.objects.filter(pk__in=normalized_selected_ids).order_by(preserved_order)
            )
        else:
            games = []
    else:
        games = list(
            GamePage.objects.filter(Q(is_hot=True) | Q(is_recommended=True) | Q(created_at__gte=recent_cutoff))
            .order_by("-is_hot", "-is_recommended", "-created_at")[:max_games]
        )

    items: list[dict[str, Any]] = []
    created_tasks = 0
    published_count = 0
    draft_count = 0
    failed_count = 0
    skipped_count = 0
    post_recheck: dict[str, Any] = {}
    normalized_rank_pool_bsn_map: dict[int, dict[str, Any]] = {}
    if isinstance(rank_pool_bsn_map, dict):
        for raw_game_id, raw_info in rank_pool_bsn_map.items():
            game_id = _safe_int(raw_game_id, default=0)
            if game_id <= 0 or not isinstance(raw_info, dict):
                continue
            bsn_value = _safe_int(raw_info.get("bsn"), default=0)
            if bsn_value <= 0:
                continue
            row = dict(raw_info)
            row["bsn"] = int(bsn_value)
            row["board_url"] = str(raw_info.get("board_url") or "").strip() or f"https://forum.gamer.com.tw/B.php?bsn={int(bsn_value)}"
            row["source"] = str(raw_info.get("source") or "bahamut_rank_pool_selected")
            normalized_rank_pool_bsn_map[game_id] = row

    requested_workers = _safe_int(parallel_workers, default=0)
    if requested_workers > 0:
        worker_count = max(1, min(8, requested_workers))
    else:
        worker_count = max(1, min(4, len(games)))

    run_in_parallel = len(games) > 1 and worker_count > 1
    worker_results: list[dict[str, Any]] = []

    if run_in_parallel:
        with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="seo-daily") as executor:
            future_map = {
                executor.submit(
                    _run_single_daily_seo_game,
                    actor=actor,
                    game=game,
                    index=index,
                    post_min=post_min,
                    post_max=post_max,
                    crawl_attempt_limit=crawl_attempt_limit,
                    rewrite_limit_value=rewrite_limit_value,
                    threshold=threshold,
                    publish_now_flag=publish_now_flag,
                    rewrite_low_quality=rewrite_low_quality,
                    rank_pool_bsn_info=normalized_rank_pool_bsn_map.get(_safe_int(getattr(game, "id", 0), default=0)),
                    enforce_rank_pool_bsn=bool(enforce_rank_pool_bsn),
                ): (index, game)
                for index, game in enumerate(games, start=1)
            }
            for future in as_completed(future_map):
                index, game = future_map[future]
                try:
                    worker_results.append(future.result())
                except Exception as exc:
                    worker_results.append(
                        {
                            "index": index,
                            "created_tasks": 0,
                            "published_count": 0,
                            "draft_count": 0,
                            "failed_count": 1,
                            "skipped_count": 0,
                            "item": {
                                "game_id": game.id,
                                "game_title": game.title,
                                "status": "failed_exception",
                                "error": str(exc)[:300],
                            },
                        }
                    )
    else:
        for index, game in enumerate(games, start=1):
            worker_results.append(
                _run_single_daily_seo_game(
                    actor=actor,
                    game=game,
                    index=index,
                    post_min=post_min,
                    post_max=post_max,
                    crawl_attempt_limit=crawl_attempt_limit,
                    rewrite_limit_value=rewrite_limit_value,
                    threshold=threshold,
                    publish_now_flag=publish_now_flag,
                    rewrite_low_quality=rewrite_low_quality,
                    rank_pool_bsn_info=normalized_rank_pool_bsn_map.get(_safe_int(getattr(game, "id", 0), default=0)),
                    enforce_rank_pool_bsn=bool(enforce_rank_pool_bsn),
                )
            )

    worker_results.sort(key=lambda row: _safe_int(row.get("index"), default=0))
    for result in worker_results:
        created_tasks += _safe_int(result.get("created_tasks"), default=0)
        published_count += _safe_int(result.get("published_count"), default=0)
        draft_count += _safe_int(result.get("draft_count"), default=0)
        failed_count += _safe_int(result.get("failed_count"), default=0)
        skipped_count += _safe_int(result.get("skipped_count"), default=0)
        item = result.get("item")
        if isinstance(item, dict):
            items.append(item)

    if post_recheck_published and publish_now_flag and games:
        try:
            post_recheck = run_published_article_recheck_automation(
                actor=actor,
                game_ids=[game.id for game in games] if games else [],
                limit=max(1, min(300, _safe_int(recheck_limit, default=120))),
                rewrite_low_quality=True,
                archive_duplicates=True,
                review_threshold=threshold,
            )
        except Exception as exc:
            post_recheck = {"status": "failed", "error": str(exc)[:260]}
    elif post_recheck_published and not publish_now_flag:
        post_recheck = {"status": "skipped_publish_status_draft"}
    elif post_recheck_published:
        post_recheck = {"status": "skipped_no_target_games"}

    return {
        "status": "completed" if failed_count == 0 else ("partial" if published_count > 0 or skipped_count > 0 else "failed"),
        "generated_at": timezone.now().isoformat(),
        "target_games": len(games),
        "created_tasks": created_tasks,
        "published_count": published_count,
        "draft_count": draft_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "max_attempts_per_game": crawl_attempt_limit,
        "rewrite_limit": rewrite_limit_value,
        "parallel_workers": worker_count,
        "execution_mode": "parallel" if run_in_parallel else "serial",
        "publish_status": normalized_publish_status,
        "rank_pool_bsn_map_count": len(normalized_rank_pool_bsn_map),
        "enforce_rank_pool_bsn": bool(enforce_rank_pool_bsn),
        "pre_import": pre_import,
        "post_recheck": post_recheck,
        "items": items,
    }


def run_published_article_recheck_automation(
    *,
    actor,
    game_ids: list[int] | None = None,
    limit: int = 100,
    rewrite_low_quality: bool = True,
    archive_duplicates: bool = True,
    review_threshold: int = 72,
) -> dict[str, Any]:
    from django.db import close_old_connections
    from seo_automation.models import SeoArticle
    from seo_automation.views import _publish_seo_article

    close_old_connections()
    try:
        threshold = max(1, min(100, _safe_int(review_threshold, default=72)))
        target_limit = max(1, min(300, _safe_int(limit, default=100)))

        queryset = (
            SeoArticle.objects.select_related("game", "task", "published_article")
            .filter(published_article__isnull=False)
            .order_by("-published_at", "-updated_at")
        )
        if game_ids:
            queryset = queryset.filter(game_id__in=game_ids)
        rows = list(queryset[:target_limit])

        rewritten_count = 0
        archived_count = 0
        healthy_count = 0
        failed_count = 0
        items: list[dict[str, Any]] = []

        for seo_article in rows:
            item: dict[str, Any] = {
                "seo_article_id": seo_article.id,
                "article_id": seo_article.published_article_id,
                "title": seo_article.title,
            }
            try:
                review = evaluate_robot_quality_for_seo_article(seo_article, threshold=threshold)
                item["review"] = review

                if review.get("duplicates") and archive_duplicates:
                    current_score = _engagement_score(seo_article.published_article)
                    best_duplicate = max(review["duplicates"], key=lambda row: _safe_int(row.get("engagement"), 0))
                    best_score = _safe_int(best_duplicate.get("engagement"), 0)
                    if best_score > current_score:
                        archived = _archive_article_if_exists(seo_article.published_article_id, reason="recheck_duplicate_lower_engagement")
                        if archived:
                            archived_count += 1
                            seo_article.status = "review"
                            seo_article.save(update_fields=["status", "updated_at"])
                            item["status"] = "archived_duplicate"
                            items.append(item)
                            continue

                if review.get("pass"):
                    healthy_count += 1
                    item["status"] = "healthy"
                    items.append(item)
                    continue

                if rewrite_low_quality:
                    rewrite_info = rewrite_low_quality_seo_article(
                        seo_article=seo_article,
                        actor=actor,
                        reason="published_recheck_low_quality",
                    )
                    _publish_seo_article(
                        seo_article=seo_article,
                        request_user=actor,
                        publish_now=True,
                        publish_at=seo_article.publish_at.isoformat() if seo_article.publish_at else None,
                    )
                    seo_article.refresh_from_db()
                    review_after = evaluate_robot_quality_for_seo_article(seo_article, threshold=threshold)
                    item["status"] = "rewritten_and_republished"
                    item["rewrite"] = rewrite_info
                    item["review_after_rewrite"] = review_after
                    rewritten_count += 1
                else:
                    item["status"] = "low_quality_needs_manual"
                    seo_article.status = "review"
                    seo_article.save(update_fields=["status", "updated_at"])
                items.append(item)
            except Exception as exc:
                failed_count += 1
                item["status"] = "failed"
                item["error"] = str(exc)[:300]
                items.append(item)

        return {
            "status": "completed" if failed_count == 0 else ("partial" if rewritten_count or healthy_count else "failed"),
            "generated_at": timezone.now().isoformat(),
            "target_count": len(rows),
            "healthy_count": healthy_count,
            "rewritten_count": rewritten_count,
            "archived_count": archived_count,
            "failed_count": failed_count,
            "items": items,
        }
    finally:
        close_old_connections()


def _normalize_rank_pool_title(value: Any) -> str:
    normalized = _normalize_for_similarity(str(value or ""))
    return re.sub(r"\s+", "", normalized)


_DAILY_MIN_RANK_CHANGE = 20


def _load_bahamut_top100_entries() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if callable(search_bahamut_entries):
        try:
            fetched = search_bahamut_entries(q="", limit=100)
            if isinstance(fetched, list):
                rows = [row for row in fetched if isinstance(row, dict)]
        except Exception:
            rows = []

    if not rows and callable(select_bahamut_entries_for_daily):
        try:
            fetched = select_bahamut_entries_for_daily(limit=100)
            if isinstance(fetched, list):
                rows = [row for row in fetched if isinstance(row, dict)]
        except Exception:
            rows = []

    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        rank = _safe_int(row.get("rank"), default=0)
        if rank <= 0 or rank > 100:
            continue
        board_title = str(row.get("board_title") or "").strip()
        if not board_title:
            continue
        normalized_rows.append(
            {
                "rank": rank,
                "rank_change": _safe_int(row.get("rank_change"), default=0),
                "board_title": board_title,
                "bsn": _safe_int(row.get("bsn"), default=0),
            }
        )
    normalized_rows.sort(key=lambda item: (item["rank"], -item["rank_change"], item["board_title"]))
    return normalized_rows


def _pick_daily_priority_rank_pool_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str | int] = set()

    for row in entries:
        rank_change = _safe_int(row.get("rank_change"), default=0)
        if rank_change < _DAILY_MIN_RANK_CHANGE:
            continue

        bsn = _safe_int(row.get("bsn"), default=0)
        key: str | int = bsn if bsn > 0 else _normalize_rank_pool_title(row.get("board_title"))
        if not key or key in seen:
            continue
        seen.add(key)
        selected.append(row)

    return selected


def _score_rank_pool_title_match(rank_title_norm: str, candidate: dict[str, Any]) -> float:
    if not rank_title_norm:
        return 0.0

    best = 0.0
    for value in (candidate.get("title_norm"), candidate.get("title_tw_norm")):
        normalized = str(value or "")
        if not normalized:
            continue
        if rank_title_norm == normalized:
            best = max(best, 1.0)
            continue
        if rank_title_norm in normalized or normalized in rank_title_norm:
            if min(len(rank_title_norm), len(normalized)) >= 3:
                best = max(best, 0.94)
            continue
        best = max(best, _similarity(rank_title_norm, normalized))
    return best



def _resolve_rank_pool_entries_to_game_ids(
    *,
    entries: list[dict[str, Any]],
    imported_game_ids: list[int],
    include_details: bool = False,
) -> list[int] | dict[str, Any]:
    from game_page.models import GamePage

    if not entries:
        return {"game_ids": [], "items": []} if include_details else []

    imported_set = {_safe_int(raw, default=0) for raw in (imported_game_ids or [])}
    imported_set = {value for value in imported_set if value > 0}

    candidates: list[dict[str, Any]] = []
    for row in GamePage.objects.exclude(status="archived").values("id", "title", "title_tw"):
        game_id = _safe_int(row.get("id"), default=0)
        if game_id <= 0:
            continue
        title = str(row.get("title") or "").strip()
        title_tw = str(row.get("title_tw") or "").strip()
        title_norm = _normalize_rank_pool_title(title)
        title_tw_norm = _normalize_rank_pool_title(title_tw)
        if not title_norm and not title_tw_norm:
            continue
        candidates.append(
            {
                "id": game_id,
                "title": title,
                "title_tw": title_tw,
                "title_norm": title_norm,
                "title_tw_norm": title_tw_norm,
                "is_imported": game_id in imported_set,
            }
        )

    selected_ids: list[int] = []
    selected_seen: set[int] = set()
    details: list[dict[str, Any]] = []

    for row in entries:
        board_title = str(row.get("board_title") or "").strip()
        detail: dict[str, Any] = {
            "rank": _safe_int(row.get("rank"), default=0),
            "rank_change": _safe_int(row.get("rank_change"), default=0),
            "board_title": board_title,
            "bsn": _safe_int(row.get("bsn"), default=0),
            "status": "",
            "game_id": None,
            "game_title": "",
            "score": 0.0,
        }

        rank_title_norm = _normalize_rank_pool_title(board_title)
        if not rank_title_norm:
            detail["status"] = "skipped_empty_board_title"
            if include_details:
                details.append(detail)
            continue

        best_id = 0
        best_score = 0.0
        best_is_imported = False
        best_title = ""
        for candidate in candidates:
            score = _score_rank_pool_title_match(rank_title_norm, candidate)
            if score <= 0:
                continue
            candidate_is_imported = bool(candidate.get("is_imported"))
            if (
                score > best_score
                or (
                    abs(score - best_score) <= 1e-6
                    and candidate_is_imported
                    and not best_is_imported
                )
            ):
                best_score = score
                best_id = _safe_int(candidate.get("id"), default=0)
                best_is_imported = candidate_is_imported
                best_title = str(candidate.get("title_tw") or candidate.get("title") or "")

        detail["score"] = round(float(best_score), 4)

        if best_id <= 0:
            detail["status"] = "skipped_no_game_match"
            if include_details:
                details.append(detail)
            continue

        detail["game_id"] = best_id
        detail["game_title"] = best_title

        if best_score < 0.66:
            detail["status"] = "skipped_low_similarity"
            if include_details:
                details.append(detail)
            continue

        if best_id in selected_seen:
            detail["status"] = "skipped_duplicate_game_match"
            if include_details:
                details.append(detail)
            continue

        selected_seen.add(best_id)
        selected_ids.append(best_id)
        detail["status"] = "selected"
        if include_details:
            details.append(detail)

    if include_details:
        return {
            "game_ids": selected_ids,
            "items": details,
        }
    return selected_ids


def _build_selected_game_rank_pool_bsn_map(
    *,
    detail_items: list[dict[str, Any]],
    selected_game_ids: list[int],
) -> dict[int, dict[str, Any]]:
    selected_set = {
        _safe_int(raw, default=0)
        for raw in (selected_game_ids or [])
        if _safe_int(raw, default=0) > 0
    }
    selected_rank_pool_bsn_map: dict[int, dict[str, Any]] = {}
    for item in detail_items or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "") != "selected":
            continue
        game_id = _safe_int(item.get("game_id"), default=0)
        bsn = _safe_int(item.get("bsn"), default=0)
        if game_id <= 0 or bsn <= 0:
            continue
        if game_id not in selected_set or game_id in selected_rank_pool_bsn_map:
            continue
        selected_rank_pool_bsn_map[game_id] = {
            "bsn": int(bsn),
            "board_url": f"https://forum.gamer.com.tw/B.php?bsn={int(bsn)}",
            "board_title": str(item.get("board_title") or "").strip(),
            "rank": _safe_int(item.get("rank"), default=0),
            "rank_change": _safe_int(item.get("rank_change"), default=0),
            "source": "bahamut_rank_pool_selected",
        }
    return selected_rank_pool_bsn_map



def _collect_daily_target_game_ids(
    *,
    imported_game_ids: list[int],
    limit_games: int,
    recent_days: int,
) -> dict[str, Any]:
    target = max(1, min(100, _safe_int(limit_games, default=6)))

    rank_pool_entries = _load_bahamut_top100_entries()
    priority_entries = _pick_daily_priority_rank_pool_entries(rank_pool_entries)
    resolution = _resolve_rank_pool_entries_to_game_ids(
        entries=priority_entries,
        imported_game_ids=imported_game_ids,
        include_details=True,
    )

    resolved_game_ids: list[int]
    detail_items: list[dict[str, Any]]
    if isinstance(resolution, dict):
        resolved_game_ids = [
            _safe_int(raw, default=0)
            for raw in (resolution.get("game_ids") or [])
            if _safe_int(raw, default=0) > 0
        ]
        detail_items = [row for row in (resolution.get("items") or []) if isinstance(row, dict)]
    else:
        resolved_game_ids = [_safe_int(raw, default=0) for raw in resolution if _safe_int(raw, default=0) > 0]
        detail_items = []

    selected_game_ids = resolved_game_ids[:target]
    selected_set = set(selected_game_ids)
    trimmed_count = max(0, len(resolved_game_ids) - len(selected_game_ids))

    if trimmed_count > 0 and detail_items:
        for item in detail_items:
            if str(item.get("status") or "") != "selected":
                continue
            game_id = _safe_int(item.get("game_id"), default=0)
            if game_id > 0 and game_id not in selected_set:
                item["status"] = "selected_but_trimmed_by_limit"

    selected_entry_count = len([item for item in detail_items if str(item.get("status") or "") == "selected"])
    unmatched_entry_count = len(
        [item for item in detail_items if str(item.get("status") or "") not in {"selected", "selected_but_trimmed_by_limit"}]
    )
    selected_game_bsn_map = _build_selected_game_rank_pool_bsn_map(
        detail_items=detail_items,
        selected_game_ids=selected_game_ids,
    )

    return {
        "status": "completed" if selected_game_ids else "skipped_no_rank_pool_match",
        "ranking_source_used": "bahamut_top100_rise20",
        "source_pool_count": len(rank_pool_entries),
        "priority_pool_count": len(priority_entries),
        "min_rank_change": _DAILY_MIN_RANK_CHANGE,
        "resolved_game_count": len(resolved_game_ids),
        "selected_game_count": len(selected_game_ids),
        "selected_game_ids": selected_game_ids,
        "selected_entry_count": selected_entry_count,
        "unmatched_entry_count": unmatched_entry_count,
        "trimmed_count": trimmed_count,
        "limit_games": target,
        "recent_days": max(1, min(120, _safe_int(recent_days, default=30))),
        "imported_game_count": len({_safe_int(raw, default=0) for raw in (imported_game_ids or []) if _safe_int(raw, default=0) > 0}),
        "selected_game_bsn_map_count": len(selected_game_bsn_map),
        "selected_game_bsn_map": selected_game_bsn_map,
        "items": detail_items,
    }



def run_daily_robot_full_cycle(
    *,
    actor=None,
    import_limit: int = 30,
    limit_games: int = 6,
    posts_min: int = 10,
    posts_max: int = 20,
    max_attempts_per_game: int = 1,
    rewrite_limit: int = 1,
    review_threshold: int = 72,
    recent_days: int = 30,
    publish_status: str = "published",
    publish_now: bool = True,
    progress_callback: Callable[[str, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    normalized_import_limit = max(1, min(100, _safe_int(import_limit, default=30)))
    normalized_limit_games = max(1, min(100, _safe_int(limit_games, default=6)))
    normalized_posts_min = max(1, min(200, _safe_int(posts_min, default=10)))
    normalized_posts_max = max(normalized_posts_min, min(200, _safe_int(posts_max, default=20)))
    normalized_max_attempts_per_game = max(1, min(5, _safe_int(max_attempts_per_game, default=1)))
    normalized_rewrite_limit = max(1, min(5, _safe_int(rewrite_limit, default=1)))
    normalized_review_threshold = max(1, min(100, _safe_int(review_threshold, default=72)))
    normalized_recent_days = max(1, min(120, _safe_int(recent_days, default=30)))
    normalized_publish_status = _normalize_publish_status(
        publish_status,
        fallback_publish_now=bool(publish_now),
    )
    publish_now_flag = normalized_publish_status == "published"

    def _emit(stage: str, detail: dict[str, Any] | None = None) -> None:
        if not callable(progress_callback):
            return
        try:
            progress_callback(stage, detail or {})
        except Exception:
            pass

    discovery_limit = max(20, normalized_import_limit * 2)
    discovery_timeout_seconds = max(
        30,
        min(
            900,
            _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_DISCOVERY_TIMEOUT_SECONDS", 240), default=240),
        ),
    )
    _emit(
        "discovery.started",
        {
            "limit": discovery_limit,
            "timeout_seconds": discovery_timeout_seconds,
        },
    )
    discovery_mode, discovery_payload, discovery_error, discovery_elapsed_ms = _run_callable_with_wall_timeout(
        lambda: discover_missing_google_play_package_ids(
            limit=discovery_limit,
            progress_callback=lambda stage, detail: _emit(f"discovery.{stage}", detail),
        ),
        timeout_seconds=discovery_timeout_seconds,
    )
    if discovery_mode == "ok" and isinstance(discovery_payload, dict):
        discovery = discovery_payload
    elif discovery_mode == "timeout":
        discovery = {
            "status": "timeout",
            "target_count": discovery_limit,
            "discovered_count": 0,
            "package_ids": [],
            "checked_seeds": [],
            "error": discovery_error,
        }
    else:
        discovery = {
            "status": "error",
            "target_count": discovery_limit,
            "discovered_count": 0,
            "package_ids": [],
            "checked_seeds": [],
            "error": discovery_error or "discovery_failed",
        }
    discovery_status = str(discovery.get("status") or "").strip().lower()
    allow_import_auto_discover = bool(not discovery.get("package_ids")) and discovery_status not in {"timeout", "error"}
    _emit(
        "discovery.completed",
        {
            "status": discovery_status,
            "target_count": _safe_int(discovery.get("target_count"), default=0),
            "discovered_count": _safe_int(discovery.get("discovered_count"), default=0),
            "elapsed_ms": discovery_elapsed_ms,
            "mode": discovery_mode,
            "error": str(discovery.get("error") or "")[:180],
        },
    )

    _emit(
        "import.started",
        {
            "limit": normalized_import_limit,
            "seed_package_count": len(discovery.get("package_ids") or []),
        },
    )
    import_result = run_google_play_import_automation(
        actor=actor,
        package_ids=list(discovery.get("package_ids") or []),
        template_key="default",
        category_id=None,
        publish_status="draft",
        overwrite_existing=False,
        limit=normalized_import_limit,
        auto_discover_missing=allow_import_auto_discover,
        progress_callback=lambda stage, detail: _emit(f"import.{stage}", detail),
    )
    _emit(
        "import.completed",
        {
            "status": str(import_result.get("status") or ""),
            "target_count": _safe_int(import_result.get("target_count"), default=0),
            "created_count": _safe_int(import_result.get("created_count"), default=0),
            "updated_count": _safe_int(import_result.get("updated_count"), default=0),
            "failed_count": _safe_int(import_result.get("failed_count"), default=0),
        },
    )

    imported_game_ids: list[int] = []
    for row in import_result.get("items") or []:
        status = str(row.get("status") or "").strip().lower()
        if status not in {"created", "updated"}:
            continue
        game_id = _safe_int(row.get("game_page_id"), default=0)
        if game_id > 0:
            imported_game_ids.append(game_id)

    _emit(
        "ranking.started",
        {
            "imported_game_count": len(imported_game_ids),
            "limit_games": normalized_limit_games,
            "recent_days": normalized_recent_days,
        },
    )
    ranking_selection = _collect_daily_target_game_ids(
        imported_game_ids=imported_game_ids,
        limit_games=normalized_limit_games,
        recent_days=normalized_recent_days,
    )
    target_game_ids = [
        _safe_int(raw, default=0)
        for raw in (ranking_selection.get("selected_game_ids") or [])
        if _safe_int(raw, default=0) > 0
    ]
    selected_game_bsn_map = _build_selected_game_rank_pool_bsn_map(
        detail_items=[row for row in (ranking_selection.get("items") or []) if isinstance(row, dict)],
        selected_game_ids=target_game_ids,
    )
    _emit(
        "ranking.completed",
        {
            "status": str(ranking_selection.get("status") or ""),
            "selected_game_count": len(target_game_ids),
            "priority_pool_count": _safe_int(ranking_selection.get("priority_pool_count"), default=0),
            "selected_with_bsn_count": len(selected_game_bsn_map),
        },
    )

    effective_limit_games = 0

    if target_game_ids:
        _emit("seo_daily.started", {"target_games": len(target_game_ids)})
        seo_result = run_seo_daily_automation(
            actor=actor,
            game_ids=target_game_ids,
            limit_games=effective_limit_games,
            posts_min=normalized_posts_min,
            posts_max=normalized_posts_max,
            max_attempts_per_game=normalized_max_attempts_per_game,
            rewrite_limit=normalized_rewrite_limit,
            publish_status=normalized_publish_status,
            publish_now=publish_now_flag,
            rewrite_low_quality=True,
            review_threshold=normalized_review_threshold,
            recent_days=normalized_recent_days,
            pre_import_missing_games=False,
            post_recheck_published=False,
            rank_pool_bsn_map=selected_game_bsn_map,
            enforce_rank_pool_bsn=True,
        )
        _emit(
            "seo_daily.completed",
            {
                "status": str(seo_result.get("status") or ""),
                "target_games": _safe_int(seo_result.get("target_games"), default=0),
                "created_tasks": _safe_int(seo_result.get("created_tasks"), default=0),
                "published_count": _safe_int(seo_result.get("published_count"), default=0),
                "draft_count": _safe_int(seo_result.get("draft_count"), default=0),
                "failed_count": _safe_int(seo_result.get("failed_count"), default=0),
            },
        )
    else:
        seo_result = {
            "status": "skipped_no_rank_pool_match",
            "generated_at": timezone.now().isoformat(),
            "target_games": 0,
            "created_tasks": 0,
            "published_count": 0,
            "draft_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "max_attempts_per_game": normalized_max_attempts_per_game,
            "rewrite_limit": normalized_rewrite_limit,
            "parallel_workers": 0,
            "execution_mode": "serial",
            "publish_status": normalized_publish_status,
            "pre_import": {"status": "skipped_disabled_for_seo_daily"},
            "post_recheck": {"status": "skipped_no_target_games"},
            "items": [],
        }
        _emit("seo_daily.skipped", {"status": "skipped_no_rank_pool_match", "target_games": 0})

    seo_result["ranking_source_used"] = str(ranking_selection.get("ranking_source_used") or "bahamut_top100_rise20")
    seo_result["ranking_candidate_count"] = _safe_int(ranking_selection.get("priority_pool_count"), default=0)
    seo_result["ranking_selected_game_count"] = len(target_game_ids)
    seo_result["ranking_selected_with_bsn_count"] = len(selected_game_bsn_map)

    review_seed = len(target_game_ids)
    review_limit = max(60, min(1200, max(1, review_seed) * 6))
    if target_game_ids and publish_now_flag:
        _emit("published_recheck.started", {"target_games": len(target_game_ids), "limit": review_limit})
        review_result = run_published_article_recheck_automation(
            actor=actor,
            game_ids=target_game_ids,
            limit=review_limit,
            rewrite_low_quality=True,
            archive_duplicates=True,
            review_threshold=normalized_review_threshold,
        )
        _emit(
            "published_recheck.completed",
            {
                "status": str(review_result.get("status") or ""),
                "rewritten_count": _safe_int(review_result.get("rewritten_count"), default=0),
                "failed_count": _safe_int(review_result.get("failed_count"), default=0),
            },
        )
    elif target_game_ids and not publish_now_flag:
        review_result = {"status": "skipped_publish_status_draft", "target_count": 0, "items": []}
        _emit("published_recheck.skipped", {"status": "skipped_publish_status_draft"})
    else:
        review_result = {"status": "skipped_no_target_games", "target_count": 0, "items": []}
        _emit("published_recheck.skipped", {"status": "skipped_no_target_games"})

    import_failed = _safe_int(import_result.get("failed_count"), default=0)
    seo_failed = _safe_int(seo_result.get("failed_count"), default=0)
    review_failed = _safe_int(review_result.get("failed_count"), default=0)
    total_failed = import_failed + seo_failed + review_failed
    has_work = (
        _safe_int(import_result.get("created_count"), 0)
        + _safe_int(import_result.get("updated_count"), 0)
        + _safe_int(seo_result.get("published_count"), 0)
        + _safe_int(seo_result.get("draft_count"), 0)
        + _safe_int(review_result.get("rewritten_count"), 0)
    ) > 0

    status_value = "completed"
    if total_failed > 0 and has_work:
        status_value = "partial"
    elif total_failed > 0 and not has_work:
        status_value = "failed"
    _emit(
        "finished",
        {
            "status": status_value,
            "failed_count": total_failed,
            "target_game_count": len(target_game_ids),
        },
    )

    return {
        "status": status_value,
        "generated_at": timezone.now().isoformat(),
        "config": {
            "import_limit": normalized_import_limit,
            "limit_games": normalized_limit_games,
            "effective_limit_games": effective_limit_games,
            "posts_min": normalized_posts_min,
            "posts_max": normalized_posts_max,
            "max_attempts_per_game": normalized_max_attempts_per_game,
            "rewrite_limit": normalized_rewrite_limit,
            "review_threshold": normalized_review_threshold,
            "recent_days": normalized_recent_days,
            "publish_status": normalized_publish_status,
            "publish_now": publish_now_flag,
        },
        "ranking_selection": ranking_selection,
        "discovery": discovery,
        "import": import_result,
        "seo_daily": seo_result,
        "published_recheck": review_result,
        "target_game_ids": target_game_ids,
        "failed_count": total_failed,
    }
