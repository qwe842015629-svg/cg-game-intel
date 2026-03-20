from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
from datetime import date
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import close_old_connections
from django.utils import timezone

from .models import DailyRobotConfig, DailyRobotRun, OperationApproval
from .services import create_audit_log, execute_approval, get_server_task_catalog, mark_approval_executed, mark_approval_failed


logger = logging.getLogger(__name__)


def _to_list(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _is_feishu_enabled() -> bool:
    return bool(getattr(settings, "FEISHU_BOT_ENABLED", False))


def _event_verify_token() -> str:
    return str(getattr(settings, "FEISHU_EVENT_VERIFY_TOKEN", "") or "").strip()


def _verify_event_token(payload: dict[str, Any]) -> bool:
    expected = _event_verify_token()
    if not expected:
        return True

    candidates = [
        payload.get("token"),
        (payload.get("header") or {}).get("token"),
        (payload.get("event") or {}).get("token"),
    ]
    present = [str(item).strip() for item in candidates if str(item or "").strip()]
    if not present:
        return True
    return any(item == expected for item in present)


def _extract_text_message(raw_content: Any) -> str:
    if isinstance(raw_content, dict):
        payload = raw_content
    else:
        try:
            payload = json.loads(str(raw_content or "{}"))
        except Exception:
            payload = {}
    return str(payload.get("text") or "").strip()


def _sanitize_command_text(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    value = re.sub(r"<at [^>]+>[^<]*</at>", " ", value, flags=re.I)
    value = value.replace("\xa0", " ").replace(chr(0xFF0F), "/")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _strip_list_prefix(text: str) -> str:
    return re.sub(r"^\s*(?:\d+\s*[\.\uFF0E?\)]|[-*])\s*", "", str(text or "").strip())


def _tokenize_command(text: str) -> list[str]:
    cleaned = _strip_list_prefix(_sanitize_command_text(text))
    if not cleaned:
        return []
    if cleaned.startswith("/"):
        cleaned = cleaned[1:]
    cleaned = cleaned.strip()
    if not cleaned:
        return []
    return [item for item in cleaned.split(" ") if item]


def _contains_any(text: str, keywords: list[str]) -> bool:
    value = str(text or "")
    lowered = value.lower()
    for kw in keywords:
        key = str(kw or "")
        if not key:
            continue
        if key in value or key.lower() in lowered:
            return True
    return False


def _extract_request_token(text: str) -> str:
    value = str(text or "")
    match = re.search(r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{8})", value, flags=re.I)
    if not match:
        return ""
    return str(match.group(1) or "").strip().lower()


def _latest_daily_request_prefix(statuses: list[str]) -> str:
    rows = OperationApproval.objects.filter(
        action=OperationApproval.ACTION_DAILY_ROBOT_RUN,
        status__in=list(statuses or []),
    ).order_by("-requested_at")
    row = rows.first()
    if not row:
        return ""
    return str(row.request_id)[:8]


def _latest_ops_request_prefix(statuses: list[str]) -> str:
    rows = OperationApproval.objects.filter(
        action=OperationApproval.ACTION_SERVER_TASK_EXEC,
        status__in=list(statuses or []),
    ).order_by("-requested_at")
    row = rows.first()
    if not row:
        return ""
    return str(row.request_id)[:8]


def _infer_natural_daily_tokens(text: str) -> list[str]:
    cleaned = _strip_list_prefix(_sanitize_command_text(text))
    if not cleaned:
        return []
    if cleaned.startswith("/"):
        return []

    token = _extract_request_token(cleaned)

    if _contains_any(cleaned, ["\u5e2e\u52a9", "help", "\u547d\u4ee4", "\u600e\u4e48\u7528", "\u5982\u4f55\u7528"]) and not _contains_any(
        cleaned,
        ["\u6267\u884c\u547d\u4ee4", "shell", "ops", "\u8fd0\u7ef4"],
    ):
        return ["daily", "help"]

    if _contains_any(cleaned, ["\u5f85\u5ba1\u6279", "\u5f85\u5904\u7406", "\u5ba1\u6279\u5217\u8868", "pending"]):
        return ["daily", "pending"]

    # Query intent: output/volume summary instead of triggering run.
    if _contains_any(
        cleaned,
        [
            "\u4ea7\u51fa",
            "\u591a\u5c11\u7bc7",
            "\u51e0\u7bc7",
            "\u5931\u8d25\u51e0\u7bc7",
            "\u6267\u884c\u4e86\u51e0\u7bc7",
            "\u4efb\u52a1\u6267\u884c\u4e86",
            "\u7edf\u8ba1",
            "\u6c47\u603b",
            "summary",
        ],
    ):
        return ["daily", "summary"]

    # Advice intent: should rerun or not.
    if _contains_any(cleaned, ["\u8981\u4e0d\u8981\u91cd\u8dd1", "\u662f\u5426\u91cd\u8dd1", "\u9700\u4e0d\u9700\u8981\u91cd\u8dd1", "\u8981\u4e0d\u8981\u91cd\u8dd1\u4efb\u52a1", "\u91cd\u8dd1\u5efa\u8bae"]):
        return ["daily", "advice"]

    if _contains_any(cleaned, ["\u9a73\u56de", "\u62d2\u7edd", "\u4e0d\u901a\u8fc7", "reject"]):
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return []
        resolved = token or _latest_daily_request_prefix(
            [OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED]
        )
        reason = ""
        reason_match = re.search(
            r"(?:\u9a73\u56de|\u62d2\u7edd|\u4e0d\u901a\u8fc7|reject)\s*(?:\u5ba1\u6279|\u7533\u8bf7|\u5355)?\s*(?:[0-9a-f-]{8,36})?\s*[:\uFF1A]?\s*(.*)$",
            cleaned,
            flags=re.I,
        )
        if reason_match:
            reason = str(reason_match.group(1) or "").strip()
        if not resolved:
            return ["daily", "reject"]
        tokens = ["daily", "reject", resolved]
        if reason:
            tokens.extend([item for item in reason.split(" ") if item])
        return tokens

    approve_hit = _contains_any(cleaned, ["\u5ba1\u6279\u901a\u8fc7", "\u6279\u51c6", "\u540c\u610f", "approve", "\u901a\u8fc7\u5ba1\u6279"])
    reject_hit = _contains_any(cleaned, ["\u9a73\u56de", "\u62d2\u7edd", "\u4e0d\u901a\u8fc7", "reject"])
    if approve_hit and not reject_hit:
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return []
        resolved = token or _latest_daily_request_prefix([OperationApproval.STATUS_PENDING])
        return ["daily", "approve", resolved] if resolved else ["daily", "approve"]

    if _contains_any(cleaned, ["\u6267\u884c\u5ba1\u6279", "\u6267\u884c\u7533\u8bf7", "execute", "exec"]) or (
        token and _contains_any(cleaned, ["\u6267\u884c", "\u5f00\u59cb\u6267\u884c", "\u7acb\u5373\u6267\u884c"])
    ):
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return []
        resolved = token or _latest_daily_request_prefix([OperationApproval.STATUS_APPROVED])
        return ["daily", "execute", resolved] if resolved else ["daily", "execute"]

    if _contains_any(cleaned, ["\u5ba1\u8ba1", "\u5065\u5eb7\u68c0\u67e5", "slug", "seo\u68c0\u67e5", "\u89c4\u8303\u68c0\u67e5"]):
        return ["daily", "audit"]

    if _contains_any(cleaned, ["\u72b6\u6001", "\u8fdb\u5ea6", "\u4eca\u65e5\u60c5\u51b5", "\u4eca\u5929\u60c5\u51b5", "\u8fd0\u884c\u60c5\u51b5", "status"]):
        return ["daily", "status"]

    if _contains_any(cleaned, ["\u53d1\u8d77\u4efb\u52a1", "\u53d1\u8d77\u4eca\u65e5\u4efb\u52a1", "\u5f00\u59cb\u4efb\u52a1", "\u5f00\u59cb\u4eca\u65e5\u4efb\u52a1", "\u8fd0\u884c\u4efb\u52a1", "\u8dd1\u4efb\u52a1", "\u89e6\u53d1\u4efb\u52a1", "\u6267\u884c\u6bcf\u65e5", "\u6267\u884c\u4eca\u5929\u4efb\u52a1", "run daily", "daily run", "\u91cd\u8dd1\u4efb\u52a1", "\u91cd\u8dd1\u4eca\u65e5\u4efb\u52a1"]):
        return ["daily", "run", "force"]

    # Generic run intent only when clearly imperative, not query/suggestion wording.
    if (
        _contains_any(cleaned, ["\u53d1\u8d77", "\u5f00\u59cb", "\u8fd0\u884c", "\u89e6\u53d1", "\u6267\u884c", "\u8dd1", "\u91cd\u8dd1", "\u91cd\u8bd5"])
        and _contains_any(cleaned, ["\u4efb\u52a1", "daily", "\u65e5\u5e38", "\u6bcf\u65e5"])
        and not _contains_any(cleaned, ["\u591a\u5c11", "\u51e0\u7bc7", "\u5931\u8d25", "\u5b8c\u6210", "\u72b6\u6001", "\u6c47\u603b", "\u7edf\u8ba1", "\u4ea7\u51fa", "\u8981\u4e0d\u8981", "\u662f\u5426", "\u9700\u4e0d\u9700\u8981", "\u5efa\u8bae"])
    ):
        return ["daily", "run", "force"]

    return []


def _infer_natural_ops_tokens(text: str) -> list[str]:
    cleaned = _strip_list_prefix(_sanitize_command_text(text))
    if not cleaned or cleaned.startswith("/"):
        return []

    token = _extract_request_token(cleaned)

    if _contains_any(cleaned, ["\u8fd0\u7ef4\u547d\u4ee4", "\u53ef\u6267\u884c\u4efb\u52a1", "\u4efb\u52a1\u5217\u8868", "ops tasks", "ops list", "\u547d\u4ee4\u5217\u8868"]):
        return ["ops", "tasks"]

    if _contains_any(cleaned, ["\u5f85\u5ba1\u6279", "\u5f85\u5904\u7406", "\u5ba1\u6279\u5217\u8868", "ops pending"]):
        return ["ops", "pending"]

    approve_hit = _contains_any(cleaned, ["\u5ba1\u6279\u901a\u8fc7", "\u6279\u51c6", "\u540c\u610f", "approve", "\u901a\u8fc7\u5ba1\u6279"] )
    reject_hit = _contains_any(cleaned, ["\u9a73\u56de", "\u62d2\u7edd", "\u4e0d\u901a\u8fc7", "reject"] )
    if approve_hit and not reject_hit:
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return ["ops", "approve", token]
        if _contains_any(cleaned, ["ops", "\u90e8\u7f72", "\u8fd0\u7ef4", "\u670d\u52a1\u5668", "\u53d1\u5e03"]):
            resolved = token or _latest_ops_request_prefix([OperationApproval.STATUS_PENDING])
            return ["ops", "approve", resolved] if resolved else ["ops", "approve"]

    if reject_hit:
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return ["ops", "reject", token]
        if _contains_any(cleaned, ["ops", "\u90e8\u7f72", "\u8fd0\u7ef4", "\u670d\u52a1\u5668", "\u53d1\u5e03"]):
            resolved = token or _latest_ops_request_prefix([OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED])
            return ["ops", "reject", resolved] if resolved else ["ops", "reject"]

    if _contains_any(cleaned, ["\u6267\u884c\u5ba1\u6279", "\u6267\u884c\u7533\u8bf7", "ops execute", "\u90e8\u7f72\u6267\u884c"]) or (
        token and _contains_any(cleaned, ["\u6267\u884c", "\u5f00\u59cb\u6267\u884c", "\u7acb\u5373\u6267\u884c"]) and _contains_any(cleaned, ["ops", "\u90e8\u7f72", "\u8fd0\u7ef4", "\u670d\u52a1\u5668", "\u53d1\u5e03"])
    ):
        if token and _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC]):
            return ["ops", "execute", token]
        resolved = token or _latest_ops_request_prefix([OperationApproval.STATUS_APPROVED, OperationApproval.STATUS_PENDING])
        return ["ops", "execute", resolved] if resolved else ["ops", "execute"]

    shell_match = re.search(r"(?:\u6267\u884c\u547d\u4ee4|shell\s+run|run\s+shell|\u6267\u884cshell)\s*[:\uFF1A]?\s*(.+)$", cleaned, flags=re.I)
    if shell_match:
        raw_cmd = str(shell_match.group(1) or "").strip()
        cmd_tokens = [item for item in re.split(r"\s+", raw_cmd) if str(item).strip()]
        if cmd_tokens:
            return ["ops", "run", "__shell__", *cmd_tokens]

    deploy_keys = [
        ("backend_restart_gunicorn", ["\u91cd\u542f\u540e\u7aef", "\u91cd\u542fgunicorn", "\u91cd\u542f\u670d\u52a1", "restart gunicorn"]),
        ("backend_check", ["\u68c0\u67e5\u540e\u7aef", "\u540e\u7aef\u68c0\u67e5", "\u5065\u5eb7\u68c0\u67e5", "backend check", "django check"]),
        ("backend_git_pull", ["\u62c9\u53d6\u540e\u7aef", "\u66f4\u65b0\u540e\u7aef\u4ee3\u7801", "backend pull", "git pull backend"]),
        ("backend_tail_gunicorn", ["\u67e5\u770b\u540e\u7aef\u65e5\u5fd7", "\u67e5\u770bgunicorn\u65e5\u5fd7", "\u540e\u7aef\u65e5\u5fd7", "gunicorn\u65e5\u5fd7"]),
    ]
    for task_key, keys in deploy_keys:
        if _contains_any(cleaned, keys):
            return ["ops", "run", task_key]

    if _contains_any(cleaned, ["\u90e8\u7f72", "\u53d1\u5e03", "\u8fd0\u7ef4", "\u670d\u52a1\u5668"]) and _contains_any(cleaned, ["\u6267\u884c", "\u5f00\u59cb", "\u89e6\u53d1", "\u8fd0\u884c"]):
        return ["ops", "tasks"]

    return []

def _looks_like_ops_intent(text: str) -> bool:
    return _contains_any(
        text,
        [
            "daily",
            "任务",
            "审批",
            "状态",
            "执行",
            "审计",
            "slug",
            "seo",
            "help",
            "帮助",
        ],
    )

def _is_llm_router_enabled() -> bool:
    raw = str(getattr(settings, "FEISHU_LLM_ROUTER_ENABLED", "true") or "true").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_active_llm_config() -> tuple[dict[str, Any], str]:
    try:
        from seo_automation.services.rewrite import _resolve_llm_config

        cfg = _resolve_llm_config() or {}
    except Exception as exc:
        return {}, f"load_llm_config_failed: {exc}"

    api_key = str(cfg.get("api_key") or "").strip()
    if not api_key:
        return {}, "llm_api_key_missing"

    base_url = str(cfg.get("base_url") or "").strip().rstrip("/")
    model = str(cfg.get("model") or "").strip()
    style = str(cfg.get("style") or "openai_chat_completions").strip().lower()
    try:
        timeout_seconds = max(10, int(cfg.get("timeout_seconds") or 45))
    except Exception:
        timeout_seconds = 45

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "style": style,
        "timeout_seconds": timeout_seconds,
    }, ""


def _llm_chat_once(*, system_prompt: str, user_prompt: str, max_tokens: int = 500, temperature: float = 0.2) -> tuple[str, str]:
    cfg, cfg_err = _load_active_llm_config()
    if cfg_err:
        return "", cfg_err

    try:
        from seo_automation.services.rewrite import (
            _build_gemini_generate_content_url,
            _build_openai_chat_url,
            _extract_gemini_text,
            _extract_openai_content,
            _post_with_auth_variants,
        )

        style = str(cfg.get("style") or "openai_chat_completions").strip().lower()
        api_key = str(cfg.get("api_key") or "").strip()
        base_url = str(cfg.get("base_url") or "").strip()
        model = str(cfg.get("model") or "").strip()
        timeout_seconds = int(cfg.get("timeout_seconds") or 45)

        if style == "gemini_generate_content":
            endpoint = _build_gemini_generate_content_url(base_url=base_url, model=model)
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"System:\n{system_prompt}\n\nUser:\n{user_prompt}"}],
                    }
                ],
                "generationConfig": {
                    "temperature": float(temperature),
                    "maxOutputTokens": int(max_tokens),
                },
            }
            response = _post_with_auth_variants(
                url=endpoint,
                payload=payload,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
                prefer_bearer=False,
            )
            if response.status_code >= 400:
                body = str(response.text or "").strip().replace("\n", " ")
                return "", f"http {response.status_code}: {body[:360]}"
            data = response.json()
            return str(_extract_gemini_text(data) or "").strip(), ""

        endpoint = _build_openai_chat_url(base_url=base_url)
        payload = {
            "model": model,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = _post_with_auth_variants(
            url=endpoint,
            payload=payload,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            prefer_bearer=True,
        )
        if response.status_code >= 400:
            body = str(response.text or "").strip().replace("\n", " ")
            return "", f"http {response.status_code}: {body[:360]}"
        data = response.json()
        return str(_extract_openai_content(data) or "").strip(), ""
    except Exception as exc:
        return "", str(exc)


def _llm_route_and_reply(text: str) -> tuple[list[str], str]:
    if not _is_llm_router_enabled():
        return [], ""

    daily_pending_prefix = _latest_daily_request_prefix([OperationApproval.STATUS_PENDING])
    daily_approved_prefix = _latest_daily_request_prefix([OperationApproval.STATUS_APPROVED])
    ops_pending_prefix = _latest_ops_request_prefix([OperationApproval.STATUS_PENDING])
    ops_approved_prefix = _latest_ops_request_prefix([OperationApproval.STATUS_APPROVED])
    task_keys = sorted((get_server_task_catalog() or {}).keys())[:20]
    task_keys_text = ",".join(task_keys) if task_keys else "-"

    system_prompt = (
        "You are a routing assistant for CypherGameBuy Feishu ops bot. "
        "Return ONLY one JSON object without markdown. "
        "Schema: {'mode':'command|chat|none','command':'','reply':''}. "
        "If user requests operational actions, output mode=command and command must be one of: "
        "daily status, daily summary, daily advice, daily audit, daily pending, daily run force, "
        "daily approve <token>, daily reject <token> <reason>, daily execute <token>, "
        "ops tasks, ops pending, ops run <task_key> [args], "
        "ops approve <token>, ops reject <token> <reason>, ops execute <token>. "
        "If user asks normal question, output mode=chat and provide concise Chinese reply in reply. "
        "If uncertain output mode=none."
    )
    user_prompt = (
        f"User text: {str(text or '').strip()}\n"
        f"Context daily pending prefix: {daily_pending_prefix or '-'}\n"
        f"Context daily approved prefix: {daily_approved_prefix or '-'}\n"
        f"Context ops pending prefix: {ops_pending_prefix or '-'}\n"
        f"Context ops approved prefix: {ops_approved_prefix or '-'}\n"
        f"Context available ops task keys: {task_keys_text}"
    )

    llm_text, llm_err = _llm_chat_once(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=420,
        temperature=0.1,
    )
    if llm_err:
        logger.warning("feishu llm route failed: %s", str(llm_err)[:240])
        err_text = str(llm_err or "")
        err_lower = err_text.lower()
        if ("insufficient_user_quota" in err_lower) or ("\u989d\u5ea6\u4e0d\u8db3" in err_text) or ("quota" in err_lower):
            return [], "\u0041\u0049 \u5df2\u63a5\u5165\uff0c\u4f46\u4e0a\u6e38\u6a21\u578b API \u4f59\u989d\u4e0d\u8db3\uff0c\u8bf7\u5145\u503c\u6216\u66f4\u6362\u53ef\u7528 Key\u3002"
        if "403" in err_lower:
            return [], "\u0041\u0049 \u5df2\u63a5\u5165\uff0c\u4f46\u5f53\u524d API Key \u6ca1\u6709\u8c03\u7528\u8be5\u6a21\u578b\u7684\u6743\u9650\uff0c\u8bf7\u68c0\u67e5\u6743\u9650\u914d\u7f6e\u3002"
        return [], "\u0041\u0049 \u8def\u7531\u6682\u65f6\u4e0d\u53ef\u7528\uff1a\u004c\u004c\u004d API \u8c03\u7528\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"
    if not llm_text:
        return [], "\u0041\u0049 \u6682\u65f6\u6ca1\u6709\u8fd4\u56de\u53ef\u89e3\u6790\u7ed3\u679c\u3002"

    try:
        from seo_automation.services.rewrite import _extract_json_object

        parsed = _extract_json_object(llm_text)
    except Exception:
        try:
            parsed = json.loads(llm_text)
        except Exception:
            plain = str(llm_text or "").strip()
            return ([], plain[:3200]) if plain else ([], "")

    if not isinstance(parsed, dict):
        return [], ""

    mode = str(parsed.get("mode") or "").strip().lower()
    command_text = str(parsed.get("command") or "").strip()
    reply_text = str(parsed.get("reply") or "").strip()

    if mode == "command" and command_text:
        normalized = command_text
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        tokens = _tokenize_command(normalized)

        if len(tokens) >= 2 and tokens[0] == "daily":
            sub = tokens[1]
            if sub == "approve" and len(tokens) < 3:
                token = daily_pending_prefix
                return (["daily", "approve", token] if token else ["daily", "approve"]), ""
            if sub == "execute" and len(tokens) < 3:
                token = daily_approved_prefix or daily_pending_prefix
                return (["daily", "execute", token] if token else ["daily", "execute"]), ""
            if sub == "reject" and len(tokens) < 3:
                token = daily_pending_prefix or daily_approved_prefix
                return (["daily", "reject", token] if token else ["daily", "reject"]), ""
            return tokens, ""

        if len(tokens) >= 2 and tokens[0] == "ops":
            sub = tokens[1]
            if sub == "approve" and len(tokens) < 3:
                token = ops_pending_prefix
                return (["ops", "approve", token] if token else ["ops", "approve"]), ""
            if sub == "execute" and len(tokens) < 3:
                token = ops_approved_prefix or ops_pending_prefix
                return (["ops", "execute", token] if token else ["ops", "execute"]), ""
            if sub == "reject" and len(tokens) < 3:
                token = ops_pending_prefix or ops_approved_prefix
                return (["ops", "reject", token] if token else ["ops", "reject"]), ""
            if sub == "run" and len(tokens) < 3 and task_keys:
                return ["ops", "run", task_keys[0]], ""
            return tokens, ""

    if mode == "chat" and reply_text:
        return [], reply_text[:3200]

    if reply_text:
        return [], reply_text[:3200]

    if mode == "none":
        return [], ""

    return [], ""

def _is_message_duplicate(message_id: str) -> bool:
    value = str(message_id or "").strip()
    if not value:
        return False
    cache_key = f"ops:feishu:msg:{value}"
    return not cache.add(cache_key, 1, timeout=600)


def _feishu_api_base() -> str:
    return str(getattr(settings, "FEISHU_API_BASE", "https://open.feishu.cn") or "https://open.feishu.cn").rstrip("/")


def _feishu_app_id() -> str:
    return str(getattr(settings, "FEISHU_APP_ID", "") or "").strip()


def _feishu_app_secret() -> str:
    return str(getattr(settings, "FEISHU_APP_SECRET", "") or "").strip()


def _get_tenant_access_token() -> tuple[str, str]:
    cache_key = "ops:feishu:tenant_access_token"
    cached = str(cache.get(cache_key) or "").strip()
    if cached:
        return cached, ""

    app_id = _feishu_app_id()
    app_secret = _feishu_app_secret()
    if not app_id or not app_secret:
        return "", "FEISHU_APP_ID / FEISHU_APP_SECRET not configured"

    url = f"{_feishu_api_base()}/open-apis/auth/v3/tenant_access_token/internal"
    try:
        response = requests.post(url, json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
    except requests.RequestException as exc:
        return "", f"tenant_access_token request failed: {exc}"

    if response.status_code >= 400:
        return "", f"tenant_access_token http {response.status_code}"

    try:
        data = response.json()
    except Exception:
        data = {}

    code = data.get("code")
    if code not in (0, "0", None):
        return "", f"tenant_access_token code={code} msg={data.get('msg')}"

    token = str(data.get("tenant_access_token") or "").strip()
    if not token:
        return "", "tenant_access_token missing"

    try:
        expire = max(300, int(data.get("expire") or 7200))
    except Exception:
        expire = 7200
    cache.set(cache_key, token, timeout=max(300, expire - 120))
    return token, ""


def _send_chat_text(chat_id: str, text: str) -> tuple[bool, str]:
    receive_id = str(chat_id or "").strip()
    body_text = str(text or "").strip()
    if not receive_id or not body_text:
        return False, "chat_id/text empty"

    token, token_err = _get_tenant_access_token()
    if not token:
        return False, token_err

    url = f"{_feishu_api_base()}/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": body_text}, ensure_ascii=False),
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code >= 400:
        return False, f"http {response.status_code}"

    try:
        data = response.json()
    except Exception:
        data = {}

    code = data.get("code")
    if code not in (0, "0", None):
        return False, f"code={code} msg={data.get('msg')}"
    return True, "ok"


def _resolve_actor_user():
    User = get_user_model()
    configured = str(getattr(settings, "OPS_GATEWAY_AUTORUN_ACTOR", "") or "").strip()
    if configured:
        user = User.objects.filter(username=configured, is_active=True).order_by("id").first()
        if user:
            return user
    user = User.objects.filter(is_superuser=True, is_active=True).order_by("id").first()
    if user:
        return user
    return User.objects.filter(is_staff=True, is_active=True).order_by("id").first()


def _requester_whitelist() -> list[str]:
    return _to_list(getattr(settings, "FEISHU_OPS_REQUESTER_OPEN_IDS", []))


def _admin_whitelist() -> list[str]:
    return _to_list(getattr(settings, "FEISHU_OPS_ADMIN_OPEN_IDS", []))


def _can_request(sender_open_id: str) -> bool:
    white = _requester_whitelist()
    if not white:
        return True
    return sender_open_id in white


def _can_admin(sender_open_id: str) -> bool:
    white = _admin_whitelist()
    if not white:
        return False
    return sender_open_id in white


def _help_text() -> str:
    return (
        "\u53ef\u7528\u547d\u4ee4\uff1a\n"
        "[Daily]\n"
        "1. /daily status \u67e5\u770b\u4eca\u65e5\u4efb\u52a1\u72b6\u6001\n"
        "2. /daily audit \u68c0\u67e5\u4eca\u65e5 SEO Slug \u5065\u5eb7\n"
        "3. /daily run [force] \u63d0\u4ea4\u4eca\u65e5\u6267\u884c\u7533\u8bf7\n"
        "4. /daily pending \u67e5\u770b\u5f85\u5904\u7406\u5ba1\u6279\n"
        "5. /daily approve <request_id|prefix8> \u5ba1\u6279\u901a\u8fc7\n"
        "6. /daily reject <request_id|prefix8> [reason] \u9a73\u56de\u7533\u8bf7\n"
        "7. /daily execute <request_id|prefix8> \u5f00\u59cb\u6267\u884c\n"
        "[Ops]\n"
        "8. /ops tasks \u67e5\u770b\u53ef\u6267\u884c\u8fd0\u7ef4\u4efb\u52a1\n"
        "9. /ops run <task_key> [args...] \u63d0\u4ea4\u8fd0\u7ef4\u6267\u884c\u7533\u8bf7\n"
        "10. /ops pending \u67e5\u770b\u5f85\u5904\u7406\u8fd0\u7ef4\u5ba1\u6279\n"
        "11. /ops approve <request_id|prefix8> \u5ba1\u6279\u901a\u8fc7\n"
        "12. /ops reject <request_id|prefix8> [reason] \u9a73\u56de\u7533\u8bf7\n"
        "13. /ops execute <request_id|prefix8> \u5f00\u59cb\u6267\u884c\n"
        "\u81ea\u7136\u8bed\u8a00\u793a\u4f8b\uff1a\u67e5\u770b\u4eca\u65e5\u72b6\u6001 / \u53d1\u8d77\u4eca\u65e5\u4efb\u52a1 / \u91cd\u542f\u540e\u7aef / \u67e5\u770b\u540e\u7aef\u65e5\u5fd7"
    )

def _resolve_approval_by_token(token: str, *, actions: list[str] | None = None):
    # Tolerate pasted token tails like Chinese punctuation from chat apps.
    raw = str(token or "").strip().lower()
    key = re.sub(r"[^0-9a-f-]", "", raw)
    if not key:
        return None

    action_values = [item for item in (actions or [OperationApproval.ACTION_DAILY_ROBOT_RUN]) if str(item).strip()]
    if not action_values:
        action_values = [OperationApproval.ACTION_DAILY_ROBOT_RUN]

    direct = None
    if len(key) >= 32 and "-" in key:
        try:
            direct = OperationApproval.objects.filter(
                action__in=action_values,
                request_id=key,
            ).first()
        except Exception:
            direct = None
    if direct:
        return direct

    rows = list(
        OperationApproval.objects.filter(action__in=action_values).order_by("-requested_at")[:200]
    )
    matched = [row for row in rows if str(row.request_id).lower().startswith(key)]
    if len(matched) == 1:
        return matched[0]
    return None


def _daily_status_text() -> str:
    from seo_automation.models import CrawlerTask

    today = date.today()
    config = DailyRobotConfig.get_solo()
    runs_today = DailyRobotRun.objects.filter(run_date=today).order_by("-started_at", "-id")
    latest = runs_today.first()
    auto_tasks = CrawlerTask.objects.filter(created_at__date=today, name__icontains="Auto Daily SEO")

    return (
        f"[每日状态] {today.isoformat()}\n"
        f"配置启用={bool(config.is_enabled)} 执行小时={int(config.daily_hour)}\n"
        f"今日运行次数={runs_today.count()} 最新状态={getattr(latest, 'status', '') or '-'}\n"
        f"最新运行ID={getattr(latest, 'id', None)} 触发来源={getattr(latest, 'trigger_source', '') or '-'}\n"
        f"今日自动任务={auto_tasks.count()} 失败={auto_tasks.filter(status='failed').count()} 完成={auto_tasks.filter(status='completed').count()}"
    )

def _daily_output_summary_text() -> str:
    from game_article.models import Article
    from seo_automation.models import CrawlerTask, SeoArticle

    def _int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    today = date.today()
    runs_today = DailyRobotRun.objects.filter(run_date=today).order_by("-started_at", "-id")
    latest = runs_today.first()

    run_summary = {}
    if latest and isinstance(getattr(latest, "summary", None), dict):
        run_summary = dict(latest.summary or {})
    if isinstance(run_summary.get("result"), dict):
        run_summary = dict(run_summary.get("result") or {})

    seo_daily = run_summary.get("seo_daily") if isinstance(run_summary.get("seo_daily"), dict) else {}
    import_result = run_summary.get("import") if isinstance(run_summary.get("import"), dict) else {}
    review_result = run_summary.get("published_recheck") if isinstance(run_summary.get("published_recheck"), dict) else {}

    auto_tasks = CrawlerTask.objects.filter(created_at__date=today, name__icontains="Auto Daily SEO")
    seo_articles_today = SeoArticle.objects.filter(created_at__date=today).count()
    published_articles_today = Article.objects.filter(status="published", published_at__date=today).count()

    return (
        f"[\u4eca\u65e5\u4ea7\u51fa] {today.isoformat()}\n"
        f"\u8fd0\u884c: \u6b21\u6570={runs_today.count()} \u6700\u65b0\u72b6\u6001={getattr(latest, 'status', '') or '-'} \u89e6\u53d1\u6765\u6e90={getattr(latest, 'trigger_source', '') or '-'}\n"
        f"SEO\u81ea\u52a8\u5316: created_tasks={_int(seo_daily.get('created_tasks'))} published={_int(seo_daily.get('published_count'))} draft={_int(seo_daily.get('draft_count'))} failed={_int(seo_daily.get('failed_count'))}\n"
        f"\u5bfc\u5165: created={_int(import_result.get('created_count'))} updated={_int(import_result.get('updated_count'))} failed={_int(import_result.get('failed_count'))}\n"
        f"\u590d\u68c0: rewritten={_int(review_result.get('rewritten_count'))} failed={_int(review_result.get('failed_count'))}\n"
        f"\u4efb\u52a1\u6267\u884c: auto_tasks={auto_tasks.count()} completed={auto_tasks.filter(status='completed').count()} failed={auto_tasks.filter(status='failed').count()}\n"
        f"\u5185\u5bb9\u7edf\u8ba1: seo_articles_today={seo_articles_today} published_articles_today={published_articles_today}"
    )


def _daily_rerun_advice_text() -> str:
    from seo_automation.models import CrawlerTask

    def _int(value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    today = date.today()
    latest = DailyRobotRun.objects.filter(run_date=today).order_by("-started_at", "-id").first()
    if not latest:
        return "\u4eca\u65e5\u8fd8\u6ca1\u6709\u8fd0\u884c\u8bb0\u5f55\uff0c\u5efa\u8bae\u5148\u6267\u884c\u4e00\u6b21\uff1a/daily run force"

    summary = {}
    if isinstance(getattr(latest, "summary", None), dict):
        summary = dict(latest.summary or {})
    if isinstance(summary.get("result"), dict):
        summary = dict(summary.get("result") or {})

    failed_count = _int(summary.get("failed_count"))
    auto_failed = CrawlerTask.objects.filter(created_at__date=today, name__icontains="Auto Daily SEO", status="failed").count()
    status_value = str(getattr(latest, "status", "") or "").lower()

    if status_value in {"running"}:
        return "\u4eca\u65e5\u4efb\u52a1\u4ecd\u5728\u8fd0\u884c\u4e2d\uff0c\u5efa\u8bae\u5148\u7b49\u5f85\u5b8c\u6210\u518d\u8bc4\u4f30\u662f\u5426\u91cd\u8dd1\u3002"

    if status_value in {"failed", "partial"} or failed_count > 0 or auto_failed > 0:
        return (
            f"\u5efa\u8bae\u91cd\u8dd1\uff1a\u5f53\u524d\u72b6\u6001={status_value or '-'}\uff0cfailed_count={failed_count}\uff0cauto_failed={auto_failed}\u3002\n"
            f"\u53ef\u6267\u884c\uff1a/daily run force"
        )

    return (
        f"\u5f53\u524d\u72b6\u6001\u6b63\u5e38\uff08{status_value or '-'}\uff09\uff0c\u4e0d\u5efa\u8bae\u91cd\u8dd1\u3002\n"
        f"\u82e5\u4f60\u521a\u4fee\u6539\u4e86\u914d\u7f6e\u6216\u5185\u5bb9\u6e90\uff0c\u53ef\u624b\u52a8\u6267\u884c\uff1a/daily run force"
    )


def _daily_audit_text() -> str:
    from django.db.models import Q
    from game_article.models import Article
    from game_page.models import GamePage
    from seo_automation.models import SeoArticle

    today = date.today()
    article_qs = Article.objects.filter(status="published", published_at__date=today)
    game_qs = GamePage.objects.filter(status="published", published_at__date=today)
    seo_qs = SeoArticle.objects.filter(status="published", published_at__date=today, published_article__isnull=False)

    article_total = article_qs.count()
    article_slug_missing = article_qs.filter(Q(slug__isnull=True) | Q(slug="")).count()
    game_total = game_qs.count()
    game_slug_missing = game_qs.filter(Q(slug__isnull=True) | Q(slug="")).count()
    seo_total = seo_qs.count()
    seo_slug_missing = seo_qs.filter(Q(published_article__slug__isnull=True) | Q(published_article__slug="")).count()

    latest_run = DailyRobotRun.objects.filter(run_date=today).order_by("-started_at", "-id").first()
    anomalies = []
    if article_slug_missing > 0:
        anomalies.append("article_slug_missing")
    if game_slug_missing > 0:
        anomalies.append("game_slug_missing")
    if seo_slug_missing > 0:
        anomalies.append("seo_linked_article_slug_missing")

    return (
        f"[每日审计] {today.isoformat()}\n"
        f"今日运行状态={getattr(latest_run, 'status', '') or 'missing'}\n"
        f"文章: 总数={article_total}, 缺失slug={article_slug_missing}\n"
        f"游戏页: 总数={game_total}, 缺失slug={game_slug_missing}\n"
        f"SEO已发布: 总数={seo_total}, 关联文章缺失slug={seo_slug_missing}\n"
        f"异常={','.join(anomalies) if anomalies else 'none'}"
    )

def _create_daily_run_approval(*, sender_open_id: str, force: bool) -> tuple[OperationApproval, bool]:
    actor = _resolve_actor_user()
    today_key = date.today().isoformat()
    idempotency_key = f"feishu_daily_run:{today_key}:{1 if force else 0}"

    existing = (
        OperationApproval.objects.filter(
            action=OperationApproval.ACTION_DAILY_ROBOT_RUN,
            idempotency_key=idempotency_key,
            status__in=[OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED],
        )
        .order_by("-requested_at")
        .first()
    )
    if existing:
        return existing, True

    payload = {
        "force": bool(force),
        "trigger_source": "feishu_approval",
        "requested_by_open_id": sender_open_id,
    }
    approval = OperationApproval.objects.create(
        action=OperationApproval.ACTION_DAILY_ROBOT_RUN,
        target_type="daily_robot_run",
        target_id=today_key,
        payload=payload,
        status=OperationApproval.STATUS_PENDING,
        risk_level=3,
        reason="Feishu requested daily run approval",
        idempotency_key=idempotency_key,
        requested_by=actor,
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
    )
    create_audit_log(
        approval=approval,
        event_type="request_created",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=approval.client_id,
        client_ip=approval.client_ip,
        request_snapshot=payload,
        result_snapshot={"status": approval.status},
        message="Feishu created daily run approval",
    )
    return approval, False


def _pending_daily_approvals_text() -> str:
    rows = list(
        OperationApproval.objects.filter(
            action=OperationApproval.ACTION_DAILY_ROBOT_RUN,
            status__in=[OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED],
        )
        .order_by("-requested_at")[:10]
    )
    if not rows:
        return "当前没有待处理审批。"

    lines = ["[待处理审批]"]
    for row in rows:
        rid = str(row.request_id)
        lines.append(
            f"- {rid[:8]} 状态={row.status} force={bool((row.payload or {}).get('force', True))} 时间={row.requested_at:%m-%d %H:%M}"
        )
    return "\n".join(lines)

def _approve_daily_request(*, sender_open_id: str, token: str) -> str:
    approval = _resolve_approval_by_token(token)
    if not approval:
        return "未找到审批单，或审批号前缀不唯一。"
    if approval.status != OperationApproval.STATUS_PENDING:
        return f"当前状态为 {approval.status}，无法审批通过。"

    actor = _resolve_actor_user()
    approval.status = OperationApproval.STATUS_APPROVED
    approval.approved_by = actor
    approval.approved_at = timezone.now()
    approval.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
    create_audit_log(
        approval=approval,
        event_type="approved",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
        result_snapshot={"status": approval.status},
        message="Feishu approved daily run",
    )
    return f"已审批通过: {approval.request_id}"

def _reject_daily_request(*, sender_open_id: str, token: str, reason: str) -> str:
    approval = _resolve_approval_by_token(token)
    if not approval:
        return "未找到审批单，或审批号前缀不唯一。"
    if approval.status not in {OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED}:
        return f"当前状态为 {approval.status}，无法驳回。"

    actor = _resolve_actor_user()
    approval.status = OperationApproval.STATUS_REJECTED
    if reason:
        approval.reason = (str(approval.reason or "") + f"\n[REJECT_NOTE] {reason}").strip()
    approval.save(update_fields=["status", "reason", "updated_at"])
    create_audit_log(
        approval=approval,
        event_type="rejected",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
        result_snapshot={"status": approval.status},
        message="Feishu rejected daily run",
    )
    return f"已驳回: {approval.request_id}"

def _execute_daily_request_worker(*, approval_id: int, sender_open_id: str, chat_id: str, lock_key: str) -> None:
    close_old_connections()
    actor = _resolve_actor_user()
    approval = OperationApproval.objects.filter(id=approval_id).first()
    if not approval:
        _send_chat_text(chat_id, "执行失败：审批记录不存在。")
        close_old_connections()
        return

    try:
        result = execute_approval(approval, actor=actor)
        mark_approval_executed(approval, result=result, actor=actor)
        create_audit_log(
            approval=approval,
            event_type="executed",
            actor=actor,
            actor_name=f"feishu:{sender_open_id}",
            client_id=f"feishu:{sender_open_id}"[:80],
            client_ip="feishu",
            request_snapshot=approval.payload,
            result_snapshot=result,
            message="Feishu executed daily run",
        )
        daily_status = str((result.get("daily_run") or {}).get("status") or "")
        _send_chat_text(chat_id, f"执行完成：{approval.request_id}\n日常任务状态={daily_status}")
    except Exception as exc:
        mark_approval_failed(approval, error_message=str(exc))
        create_audit_log(
            approval=approval,
            event_type="failed",
            actor=actor,
            actor_name=f"feishu:{sender_open_id}",
            client_id=f"feishu:{sender_open_id}"[:80],
            client_ip="feishu",
            request_snapshot=approval.payload,
            result_snapshot={"error": str(exc)},
            message="Feishu execution failed",
        )
        _send_chat_text(chat_id, f"执行失败：{approval.request_id}\n错误={str(exc)[:300]}")
    finally:
        if lock_key:
            cache.delete(lock_key)
        close_old_connections()

def _execute_daily_request_async(*, sender_open_id: str, chat_id: str, token: str) -> str:
    approval = _resolve_approval_by_token(token)
    if not approval:
        return "未找到审批单，或审批号前缀不唯一。"
    if approval.status == OperationApproval.STATUS_EXECUTED:
        return f"该审批已执行：{approval.request_id}"
    if approval.status != OperationApproval.STATUS_APPROVED:
        return f"当前状态为 {approval.status}，请先审批通过。"

    lock_key = f"ops:feishu:exec:{approval.request_id}"
    if not cache.add(lock_key, 1, timeout=3600):
        return f"该审批正在执行中：{approval.request_id}"

    worker = threading.Thread(
        target=_execute_daily_request_worker,
        kwargs={
            "approval_id": int(approval.id),
            "sender_open_id": sender_open_id,
            "chat_id": chat_id,
            "lock_key": lock_key,
        },
        name=f"feishu-daily-exec-{approval.id}",
        daemon=True,
    )
    worker.start()
    return f"已开始执行：{approval.request_id}。\n最终结果会自动回传到当前会话。"

def _dispatch_daily_command(tokens: list[str], *, sender_open_id: str, chat_id: str) -> str:
    if len(tokens) == 1:
        return _help_text()

    sub = str(tokens[1] or "").strip().lower()
    if sub in {"status", "stats"}:
        return _daily_status_text()
    if sub in {"summary", "report", "output"}:
        return _daily_output_summary_text()
    if sub in {"advice", "rerun_advice", "rerun"}:
        return _daily_rerun_advice_text()
    if sub in {"audit"}:
        return _daily_audit_text()
    if sub in {"pending", "list"}:
        return _pending_daily_approvals_text()

    if sub in {"run", "start"}:
        if not _can_request(sender_open_id):
            return "你没有执行申请权限，请将 open_id 加入 FEISHU_OPS_REQUESTER_OPEN_IDS。"
        force = any(str(item).strip().lower() == "force" for item in tokens[2:])
        approval, reused = _create_daily_run_approval(sender_open_id=sender_open_id, force=(force or True))
        reused_text = "复用已有审批" if reused else "已创建审批"
        return (
            f"{reused_text}: request_id={approval.request_id} status={approval.status}\n"
            f"下一步: /daily approve {str(approval.request_id)[:8]}"
        )

    if sub in {"approve"}:
        if not _can_admin(sender_open_id):
            return "你没有审批权限，请配置 FEISHU_OPS_ADMIN_OPEN_IDS。"
        if len(tokens) < 3:
            return "用法: /daily approve <request_id|prefix8>"
        return _approve_daily_request(sender_open_id=sender_open_id, token=tokens[2])

    if sub in {"reject"}:
        if not _can_admin(sender_open_id):
            return "你没有驳回权限，请配置 FEISHU_OPS_ADMIN_OPEN_IDS。"
        if len(tokens) < 3:
            return "用法: /daily reject <request_id|prefix8> [reason]"
        reason = " ".join(tokens[3:]).strip()
        return _reject_daily_request(sender_open_id=sender_open_id, token=tokens[2], reason=reason)

    if sub in {"execute", "exec"}:
        if not _can_admin(sender_open_id):
            return "你没有执行权限，请配置 FEISHU_OPS_ADMIN_OPEN_IDS。"
        if len(tokens) < 3:
            return "用法: /daily execute <request_id|prefix8>"
        return _execute_daily_request_async(sender_open_id=sender_open_id, chat_id=chat_id, token=tokens[2])

    if sub in {"help"}:
        return _help_text()

    return "未知的 daily 命令。\n" + _help_text()



def _ops_help_text() -> str:
    return (
        "Ops commands:\n"
        "1. /ops tasks list available tasks\n"
        "2. /ops run <task_key> [args...] create approval\n"
        "3. /ops pending list pending approvals\n"
        "4. /ops approve <request_id|prefix8> approve request\n"
        "5. /ops reject <request_id|prefix8> [reason] reject request\n"
        "6. /ops execute <request_id|prefix8> execute approved request\n"
        "Natural language examples: restart backend / show gunicorn logs / pull backend code"
    )

def _ops_tasks_catalog_text() -> str:
    catalog = get_server_task_catalog() or {}
    if not catalog:
        return "No server tasks configured. Please set FEISHU_OPS_TASKS_JSON."

    lines = ["[Ops Task Catalog]"]
    for task_key in sorted(catalog.keys()):
        item = catalog.get(task_key) or {}
        desc = str(item.get("description") or task_key)
        risk = int(item.get("risk_level") or 3)
        lines.append(f"- {task_key} (risk={risk}) {desc}")
    if bool(getattr(settings, "FEISHU_OPS_SHELL_ENABLED", False)):
        lines.append("- __shell__ (risk=5) custom shell command")
        lines.append("  usage: /ops run __shell__ <command...>")
    lines.append("usage: /ops run <task_key> [args...]")
    return "\n".join(lines)


def _create_ops_task_approval(*, sender_open_id: str, task_key: str, args_tokens: list[str]) -> tuple[OperationApproval | None, bool, str]:
    safe_args = [str(item).strip() for item in list(args_tokens or []) if str(item).strip()][:40]

    if task_key == "__shell__":
        if not bool(getattr(settings, "FEISHU_OPS_SHELL_ENABLED", False)):
            return None, False, "Custom shell command is disabled. Set FEISHU_OPS_SHELL_ENABLED=true first."
        if not safe_args:
            return None, False, "Usage: /ops run __shell__ <command...>"
        spec = {"risk_level": 5, "description": "custom shell command"}
    else:
        catalog = get_server_task_catalog() or {}
        spec = catalog.get(task_key)
        if not spec:
            return None, False, f"Task not found: {task_key}. Run /ops tasks to list available tasks."

    actor = _resolve_actor_user()
    args_sig = " ".join(safe_args)
    digest = hashlib.sha1(f"{task_key}|{args_sig}".encode("utf-8")).hexdigest()[:12]
    idempotency_key = f"feishu_ops_task:{task_key}:{digest}:{date.today().isoformat()}"

    existing = (
        OperationApproval.objects.filter(
            action=OperationApproval.ACTION_SERVER_TASK_EXEC,
            idempotency_key=idempotency_key,
            status__in=[OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED],
        )
        .order_by("-requested_at")
        .first()
    )
    if existing:
        return existing, True, ""

    payload = {
        "task_key": task_key,
        "args_tokens": safe_args,
        "requested_by_open_id": sender_open_id,
    }
    if task_key == "__shell__":
        payload["shell_command"] = " ".join(safe_args)

    approval = OperationApproval.objects.create(
        action=OperationApproval.ACTION_SERVER_TASK_EXEC,
        target_type="server_task",
        target_id=task_key,
        payload=payload,
        status=OperationApproval.STATUS_PENDING,
        risk_level=int(spec.get("risk_level") or 3),
        reason=f"Feishu requested server task approval: {task_key}",
        idempotency_key=idempotency_key,
        requested_by=actor,
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
    )
    create_audit_log(
        approval=approval,
        event_type="request_created",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=approval.client_id,
        client_ip=approval.client_ip,
        request_snapshot=payload,
        result_snapshot={"status": approval.status},
        message=f"Feishu created server task approval: {task_key}",
    )
    return approval, False, ""


def _pending_ops_approvals_text() -> str:
    rows = list(
        OperationApproval.objects.filter(
            action=OperationApproval.ACTION_SERVER_TASK_EXEC,
            status__in=[OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED],
        )
        .order_by("-requested_at")[:10]
    )
    if not rows:
        return "No pending ops approvals."

    lines = ["[Pending Ops Approvals]"]
    for row in rows:
        rid = str(row.request_id)
        payload = row.payload or {}
        task_key = str(payload.get("task_key") or row.target_id or "-")
        arg_text = " ".join([str(x) for x in (payload.get("args_tokens") or []) if str(x).strip()])[:80]
        lines.append(f"- {rid[:8]} status={row.status} task={task_key} args={arg_text or '-'} time={row.requested_at:%m-%d %H:%M}")
    return "\n".join(lines)


def _approve_ops_request(*, sender_open_id: str, token: str) -> str:
    approval = _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC])
    if not approval:
        return "Ops approval not found, or token prefix is not unique."
    if approval.status != OperationApproval.STATUS_PENDING:
        return f"Current status is {approval.status}; cannot approve."

    actor = _resolve_actor_user()
    approval.status = OperationApproval.STATUS_APPROVED
    approval.approved_by = actor
    approval.approved_at = timezone.now()
    approval.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
    create_audit_log(
        approval=approval,
        event_type="approved",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
        result_snapshot={"status": approval.status},
        message="Feishu approved server task",
    )
    return f"Approved: {approval.request_id}"


def _reject_ops_request(*, sender_open_id: str, token: str, reason: str) -> str:
    approval = _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC])
    if not approval:
        return "Ops approval not found, or token prefix is not unique."
    if approval.status not in {OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED}:
        return f"Current status is {approval.status}; cannot reject."

    actor = _resolve_actor_user()
    approval.status = OperationApproval.STATUS_REJECTED
    if reason:
        approval.reason = (str(approval.reason or "") + f"\n[REJECT_NOTE] {reason}").strip()
    approval.save(update_fields=["status", "reason", "updated_at"])
    create_audit_log(
        approval=approval,
        event_type="rejected",
        actor=actor,
        actor_name=f"feishu:{sender_open_id}",
        client_id=f"feishu:{sender_open_id}"[:80],
        client_ip="feishu",
        result_snapshot={"status": approval.status},
        message="Feishu rejected server task",
    )
    return f"Rejected: {approval.request_id}"


def _execute_ops_request_worker(*, approval_id: int, sender_open_id: str, chat_id: str, lock_key: str) -> None:
    close_old_connections()
    actor = _resolve_actor_user()
    approval = OperationApproval.objects.filter(id=approval_id).first()
    if not approval:
        _send_chat_text(chat_id, "Execution failed: approval record not found.")
        close_old_connections()
        return

    try:
        result = execute_approval(approval, actor=actor)
        mark_approval_executed(approval, result=result, actor=actor)
        create_audit_log(
            approval=approval,
            event_type="executed",
            actor=actor,
            actor_name=f"feishu:{sender_open_id}",
            client_id=f"feishu:{sender_open_id}"[:80],
            client_ip="feishu",
            request_snapshot=approval.payload,
            result_snapshot=result,
            message="Feishu executed server task",
        )
        task_key = str((approval.payload or {}).get("task_key") or approval.target_id or "-")
        stdout_text = str(result.get("stdout") or "").strip()
        out_brief = stdout_text[:900] if stdout_text else "(no output)"
        _send_chat_text(chat_id, f"Executed: {approval.request_id}\nTask={task_key}\nOutput:\n{out_brief}")
    except Exception as exc:
        mark_approval_failed(approval, error_message=str(exc))
        create_audit_log(
            approval=approval,
            event_type="failed",
            actor=actor,
            actor_name=f"feishu:{sender_open_id}",
            client_id=f"feishu:{sender_open_id}"[:80],
            client_ip="feishu",
            request_snapshot=approval.payload,
            result_snapshot={"error": str(exc)},
            message="Feishu execution failed",
        )
        _send_chat_text(chat_id, f"Execution failed: {approval.request_id}\nError={str(exc)[:300]}")
    finally:
        if lock_key:
            cache.delete(lock_key)
        close_old_connections()


def _execute_ops_request_async(*, sender_open_id: str, chat_id: str, token: str) -> str:
    approval = _resolve_approval_by_token(token, actions=[OperationApproval.ACTION_SERVER_TASK_EXEC])
    if not approval:
        return "Ops approval not found, or token prefix is not unique."
    if approval.status == OperationApproval.STATUS_EXECUTED:
        return f"Already executed: {approval.request_id}"
    if approval.status != OperationApproval.STATUS_APPROVED:
        return f"Current status is {approval.status}. Please approve first."

    lock_key = f"ops:feishu:exec:{approval.request_id}"
    if not cache.add(lock_key, 1, timeout=3600):
        return f"This approval is already running: {approval.request_id}"

    worker = threading.Thread(
        target=_execute_ops_request_worker,
        kwargs={
            "approval_id": int(approval.id),
            "sender_open_id": sender_open_id,
            "chat_id": chat_id,
            "lock_key": lock_key,
        },
        name=f"feishu-ops-exec-{approval.id}",
        daemon=True,
    )
    worker.start()
    return f"Execution started: {approval.request_id}. Final result will be sent to this chat."


def _dispatch_ops_command(tokens: list[str], *, sender_open_id: str, chat_id: str) -> str:
    if len(tokens) == 1:
        return _ops_help_text()

    sub = str(tokens[1] or "").strip().lower()
    if sub in {"tasks", "list"}:
        return _ops_tasks_catalog_text()
    if sub in {"pending"}:
        return _pending_ops_approvals_text()

    if sub in {"run", "start"}:
        if not _can_request(sender_open_id):
            return "You do not have requester permission. Add your open_id to FEISHU_OPS_REQUESTER_OPEN_IDS."
        if len(tokens) < 3:
            return "Usage: /ops run <task_key> [args...]"
        task_key = str(tokens[2] or "").strip()
        args_tokens = [str(item).strip() for item in tokens[3:] if str(item).strip()]
        approval, reused, err = _create_ops_task_approval(sender_open_id=sender_open_id, task_key=task_key, args_tokens=args_tokens)
        if err:
            return err
        if not approval:
            return "Failed to create ops approval."
        reused_text = "Reused approval" if reused else "Created approval"
        return (
            f"{reused_text}: request_id={approval.request_id} status={approval.status}\n"
            f"Next: /ops approve {str(approval.request_id)[:8]}"
        )

    if sub in {"approve"}:
        if not _can_admin(sender_open_id):
            return "You do not have admin permission. Configure FEISHU_OPS_ADMIN_OPEN_IDS."
        if len(tokens) < 3:
            return "Usage: /ops approve <request_id|prefix8>"
        return _approve_ops_request(sender_open_id=sender_open_id, token=tokens[2])

    if sub in {"reject"}:
        if not _can_admin(sender_open_id):
            return "You do not have admin permission. Configure FEISHU_OPS_ADMIN_OPEN_IDS."
        if len(tokens) < 3:
            return "Usage: /ops reject <request_id|prefix8> [reason]"
        reason = " ".join(tokens[3:]).strip()
        return _reject_ops_request(sender_open_id=sender_open_id, token=tokens[2], reason=reason)

    if sub in {"execute", "exec"}:
        if not _can_admin(sender_open_id):
            return "You do not have admin permission. Configure FEISHU_OPS_ADMIN_OPEN_IDS."
        if len(tokens) < 3:
            return "Usage: /ops execute <request_id|prefix8>"
        return _execute_ops_request_async(sender_open_id=sender_open_id, chat_id=chat_id, token=tokens[2])

    if sub in {"help"}:
        return _ops_help_text()

    return "Unknown ops command.\n" + _ops_help_text()

def _dispatch_command_text(text: str, *, sender_open_id: str, chat_id: str) -> str:
    # 1) Explicit command mode, e.g. /daily status or /ops tasks.
    tokens = _tokenize_command(text)
    if tokens:
        head = str(tokens[0] or "").strip().lower()
        if head in {"help", "h", "?"}:
            return _help_text()
        if head in {"daily"}:
            return _dispatch_daily_command(tokens, sender_open_id=sender_open_id, chat_id=chat_id)
        if head in {"ops"}:
            return _dispatch_ops_command(tokens, sender_open_id=sender_open_id, chat_id=chat_id)

    # 2) Rule-based natural-language mode.
    nl_tokens = _infer_natural_daily_tokens(text)
    if nl_tokens and str(nl_tokens[0] or "").strip().lower() == "daily":
        return _dispatch_daily_command(nl_tokens, sender_open_id=sender_open_id, chat_id=chat_id)

    ops_nl_tokens = _infer_natural_ops_tokens(text)
    if ops_nl_tokens and str(ops_nl_tokens[0] or "").strip().lower() == "ops":
        return _dispatch_ops_command(ops_nl_tokens, sender_open_id=sender_open_id, chat_id=chat_id)

    # 3) LLM routing + chat mode (uses active server LLM API config).
    llm_tokens, llm_reply = _llm_route_and_reply(text)
    if llm_tokens:
        head = str(llm_tokens[0] or "").strip().lower()
        if head == "daily":
            return _dispatch_daily_command(llm_tokens, sender_open_id=sender_open_id, chat_id=chat_id)
        if head == "ops":
            return _dispatch_ops_command(llm_tokens, sender_open_id=sender_open_id, chat_id=chat_id)
    if llm_reply:
        return llm_reply

    # 4) Friendly fallback.
    if _looks_like_ops_intent(text):
        return "I can help with daily tasks and ops tasks. Try: /daily status or /ops tasks."
    return ""

def handle_feishu_event_callback(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if not isinstance(payload, dict):
        return 400, {"code": 400, "msg": "invalid payload"}

    if not _verify_event_token(payload):
        return 403, {"code": 403, "msg": "verify token mismatch"}

    if str(payload.get("type") or "").strip() == "url_verification":
        return 200, {"challenge": payload.get("challenge", "")}
    if payload.get("challenge") and not payload.get("event"):
        return 200, {"challenge": payload.get("challenge", "")}

    if not _is_feishu_enabled():
        return 200, {"code": 0, "msg": "feishu bot disabled"}

    header = payload.get("header") or {}
    event_type = str(header.get("event_type") or "").strip()
    if event_type != "im.message.receive_v1":
        return 200, {"code": 0}

    event = payload.get("event") or {}
    sender = event.get("sender") or {}
    sender_type = str(sender.get("sender_type") or "").strip().lower()
    if sender_type == "app":
        return 200, {"code": 0}

    message = event.get("message") or {}
    if str(message.get("message_type") or "").strip().lower() != "text":
        return 200, {"code": 0}

    message_id = str(message.get("message_id") or "").strip()
    if _is_message_duplicate(message_id):
        return 200, {"code": 0, "msg": "duplicate"}

    chat_id = str(message.get("chat_id") or "").strip()
    sender_id = sender.get("sender_id") or {}
    sender_open_id = str(sender_id.get("open_id") or sender_id.get("user_id") or "").strip()
    text = _extract_text_message(message.get("content"))

    reply = _dispatch_command_text(text, sender_open_id=sender_open_id, chat_id=chat_id)
    if reply and chat_id:
        _send_chat_text(chat_id, reply[:3500])

    return 200, {"code": 0}
