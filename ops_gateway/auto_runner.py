from __future__ import annotations

from datetime import timedelta
import logging
import os
import sys
import threading
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

from .bahamut_ranking import refresh_bahamut_board_rankings
from .models import DailyRobotConfig, DailyRobotRun
from .services import run_daily_robot_full_cycle


logger = logging.getLogger(__name__)


def _to_list(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _post_feishu_webhook(url: str, message: str, timeout_sec: int = 10) -> tuple[bool, str]:
    payload = {"msg_type": "text", "content": {"text": message}}
    try:
        response = requests.post(url, json=payload, timeout=timeout_sec)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code >= 400:
        return False, f"http {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        data = {}

    if isinstance(data, dict):
        code = data.get("code")
        status_code = data.get("StatusCode")
        if code not in (None, 0, "0") and status_code not in (None, 0):
            return False, f"code={code} status_code={status_code} msg={data.get('msg') or data.get('StatusMessage')}"
    return True, "ok"


def _notify_daily_result_webhooks(*, run_row: DailyRobotRun | None, payload: dict[str, Any]) -> None:
    urls = _to_list(getattr(settings, "FEISHU_OPS_ALERT_WEBHOOKS", []))
    if not urls:
        return

    if run_row is None:
        run_id = "-"
        run_date = "-"
        run_status = str(payload.get("status") or "")
    else:
        run_id = str(getattr(run_row, "id", "-") or "-")
        run_date = str(getattr(run_row, "run_date", "-") or "-")
        run_status = str(getattr(run_row, "status", "") or "")

    summary_status = str(payload.get("status") or "")
    text = (
        "[Cypher Daily Task]"
        f" run_id={run_id}"
        f" run_date={run_date}"
        f" run_status={run_status}"
        f" result_status={summary_status}"
    )

    for url in urls:
        ok, detail = _post_feishu_webhook(url, text, timeout_sec=10)
        if not ok:
            logger.warning("ops_gateway feishu webhook notify failed url=%s detail=%s", url, detail)


_RUNNER_LOCK = threading.Lock()
_RUNNER_THREAD: threading.Thread | None = None
_STOP_EVENT = threading.Event()


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _normalize_publish_status(raw_status: Any, *, fallback_publish_now: bool) -> str:
    value = str(raw_status or "").strip().lower()
    if value in {"published", "draft"}:
        return value
    return "published" if bool(fallback_publish_now) else "draft"


def _base_runtime_daily_config() -> dict[str, Any]:
    posts_min = max(1, min(200, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_POSTS_MIN", 10), 10)))
    posts_max = max(posts_min, min(200, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_POSTS_MAX", 20), 20)))
    max_attempts_per_game = max(
        1,
        min(5, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_MAX_ATTEMPTS_PER_GAME", 1), 1)),
    )
    rewrite_limit = max(1, min(5, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_REWRITE_LIMIT", 1), 1)))
    fallback_publish_now = bool(getattr(settings, "OPS_GATEWAY_AUTORUN_PUBLISH_NOW", True))
    publish_status = _normalize_publish_status(
        getattr(settings, "OPS_GATEWAY_AUTORUN_PUBLISH_STATUS", ""),
        fallback_publish_now=fallback_publish_now,
    )
    return {
        "source": "settings",
        "is_enabled": bool(getattr(settings, "OPS_GATEWAY_AUTORUN_ENABLED", True)),
        "daily_hour": max(0, min(23, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_DAILY_HOUR", 4), 4))),
        "poll_seconds": max(60, min(24 * 60 * 60, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_POLL_SECONDS", 900), 900))),
        "max_running_minutes": max(
            10,
            min(24 * 60, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_MAX_RUNNING_MINUTES", 180), 180)),
        ),
        "import_limit": max(1, min(100, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_IMPORT_LIMIT", 30), 30))),
        "limit_games": max(1, min(100, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_LIMIT_GAMES", 6), 6))),
        "posts_min": posts_min,
        "posts_max": posts_max,
        "max_attempts_per_game": max_attempts_per_game,
        "rewrite_limit": rewrite_limit,
        "review_threshold": max(
            1,
            min(100, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_REVIEW_THRESHOLD", 78), 78)),
        ),
        "recent_days": max(1, min(120, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_RECENT_DAYS", 30), 30))),
        "publish_status": publish_status,
        "publish_now": publish_status == "published",
        "actor_username": str(getattr(settings, "OPS_GATEWAY_AUTORUN_ACTOR", "") or "").strip(),
    }


def _load_runtime_daily_config() -> dict[str, Any]:
    runtime = _base_runtime_daily_config()
    try:
        config_obj = DailyRobotConfig.get_solo()
    except (OperationalError, ProgrammingError):
        runtime["source"] = "settings_db_unavailable"
        return runtime
    except Exception:
        logger.exception("ops_gateway failed to load DailyRobotConfig, using settings fallback")
        runtime["source"] = "settings_db_error"
        return runtime

    posts_min = max(1, min(200, _safe_int(getattr(config_obj, "posts_min", runtime["posts_min"]), runtime["posts_min"])))
    posts_max = max(
        posts_min,
        min(200, _safe_int(getattr(config_obj, "posts_max", runtime["posts_max"]), runtime["posts_max"])),
    )
    max_attempts_per_game = max(
        1,
        min(
            5,
            _safe_int(
                getattr(config_obj, "max_attempts_per_game", runtime["max_attempts_per_game"]),
                runtime["max_attempts_per_game"],
            ),
        ),
    )
    rewrite_limit = max(
        1,
        min(5, _safe_int(getattr(config_obj, "rewrite_limit", runtime["rewrite_limit"]), runtime["rewrite_limit"])),
    )
    actor_username = str(getattr(config_obj, "actor_username", "") or "").strip()
    config_publish_now = bool(getattr(config_obj, "publish_now", runtime["publish_now"]))
    config_publish_status = _normalize_publish_status(
        getattr(config_obj, "publish_status", ""),
        fallback_publish_now=config_publish_now,
    )
    runtime.update(
        {
            "source": "db",
            "is_enabled": bool(getattr(config_obj, "is_enabled", runtime["is_enabled"])),
            "daily_hour": max(0, min(23, _safe_int(getattr(config_obj, "daily_hour", runtime["daily_hour"]), runtime["daily_hour"]))),
            "poll_seconds": max(
                60,
                min(
                    24 * 60 * 60,
                    _safe_int(getattr(config_obj, "poll_seconds", runtime["poll_seconds"]), runtime["poll_seconds"]),
                ),
            ),
            "max_running_minutes": max(
                10,
                min(
                    24 * 60,
                    _safe_int(
                        getattr(config_obj, "max_running_minutes", runtime["max_running_minutes"]),
                        runtime["max_running_minutes"],
                    ),
                ),
            ),
            "import_limit": max(
                1,
                min(100, _safe_int(getattr(config_obj, "import_limit", runtime["import_limit"]), runtime["import_limit"])),
            ),
            "limit_games": max(
                1,
                min(100, _safe_int(getattr(config_obj, "limit_games", runtime["limit_games"]), runtime["limit_games"])),
            ),
            "posts_min": posts_min,
            "posts_max": posts_max,
            "max_attempts_per_game": max_attempts_per_game,
            "rewrite_limit": rewrite_limit,
            "review_threshold": max(
                1,
                min(
                    100,
                    _safe_int(
                        getattr(config_obj, "review_threshold", runtime["review_threshold"]),
                        runtime["review_threshold"],
                    ),
                ),
            ),
            "recent_days": max(
                1,
                min(120, _safe_int(getattr(config_obj, "recent_days", runtime["recent_days"]), runtime["recent_days"])),
            ),
            "publish_status": config_publish_status,
            "publish_now": config_publish_status == "published",
            "actor_username": actor_username or runtime["actor_username"],
        }
    )
    return runtime


def _running_timeout_minutes(runtime_config: dict[str, Any] | None = None) -> int:
    if runtime_config and "max_running_minutes" in runtime_config:
        return max(10, min(24 * 60, _safe_int(runtime_config.get("max_running_minutes"), 180)))
    return max(10, min(24 * 60, _safe_int(getattr(settings, "OPS_GATEWAY_AUTORUN_MAX_RUNNING_MINUTES", 180), 180)))


def _is_stale_running(row: DailyRobotRun, *, now_dt, runtime_config: dict[str, Any] | None = None) -> bool:
    if row is None or str(getattr(row, "status", "")) != DailyRobotRun.STATUS_RUNNING:
        return False
    started_at = getattr(row, "started_at", None)
    max_seconds = _running_timeout_minutes(runtime_config) * 60
    if not started_at:
        updated_at = getattr(row, "updated_at", None)
        if not updated_at:
            return True
        elapsed = (now_dt - updated_at).total_seconds()
        return elapsed >= max_seconds
    elapsed = (now_dt - started_at).total_seconds()
    return elapsed >= max_seconds


def _mark_stale_daily_runs(*, now_dt, runtime_config: dict[str, Any] | None = None) -> int:
    stale_count = 0
    timeout_seconds = _running_timeout_minutes(runtime_config) * 60
    stale_before = now_dt - timedelta(seconds=timeout_seconds)
    rollover_grace_minutes = 45
    manual_grace_minutes = 45
    rollover_grace_before = now_dt - timedelta(minutes=rollover_grace_minutes)
    manual_grace_before = now_dt - timedelta(minutes=manual_grace_minutes)
    today = now_dt.date()

    rows = list(DailyRobotRun.objects.filter(status=DailyRobotRun.STATUS_RUNNING).order_by("started_at", "id")[:500])
    for row in rows:
        started_at = getattr(row, "started_at", None)
        updated_at = getattr(row, "updated_at", None)
        run_key_value = str(getattr(row, "run_key", "") or "")
        trigger_source_value = str(getattr(row, "trigger_source", "") or "").lower()
        row_run_date = getattr(row, "run_date", None)
        if (
            started_at is not None
            and started_at <= manual_grace_before
            and ("_manual_" in run_key_value or trigger_source_value == "management_command")
        ):
            is_stale = True
        elif row_run_date and row_run_date < today:
            if started_at is None:
                is_stale = True
            else:
                is_stale = started_at <= rollover_grace_before
        elif started_at is not None:
            is_stale = started_at <= stale_before
        elif updated_at is not None:
            is_stale = updated_at <= stale_before
        else:
            is_stale = True
        if not is_stale:
            continue

        marker = "stale_running_timeout"
        base_error = str(getattr(row, "error_message", "") or "").strip()
        if marker in base_error:
            next_error = base_error
        elif base_error:
            next_error = f"{base_error}; {marker}"[:2000]
        else:
            next_error = marker

        row.status = DailyRobotRun.STATUS_FAILED
        summary = row.summary if isinstance(row.summary, dict) else {}
        summary["status"] = DailyRobotRun.STATUS_FAILED
        summary["run_stage"] = str(summary.get("run_stage") or "stale_timeout_unresolved")
        summary["error"] = next_error
        summary["stale_marker"] = marker
        summary["stale_marked_at"] = now_dt.isoformat()
        row.summary = summary
        row.error_message = next_error
        row.finished_at = now_dt
        row.save(update_fields=["status", "summary", "error_message", "finished_at", "updated_at"])
        stale_count += 1
    return stale_count


def _mark_stale_crawler_tasks(*, now_dt, runtime_config: dict[str, Any] | None = None) -> int:
    from seo_automation.models import CrawlerTask

    stale_count = 0
    timeout_seconds = _running_timeout_minutes(runtime_config) * 60
    stale_before = now_dt - timedelta(seconds=timeout_seconds)
    active_statuses = ["pending", "crawling", "rewriting", "enriching", "seoing", "publishing"]

    rows = list(CrawlerTask.objects.filter(status__in=active_statuses).order_by("updated_at", "id")[:1000])
    for row in rows:
        started_at = getattr(row, "started_at", None)
        updated_at = getattr(row, "updated_at", None)
        if started_at is not None:
            is_stale = started_at <= stale_before
        elif updated_at is not None:
            is_stale = updated_at <= stale_before
        else:
            is_stale = False
        if not is_stale:
            continue

        marker = "stale_pipeline_timeout"
        base_error = str(getattr(row, "error_message", "") or "").strip()
        if marker in base_error:
            next_error = base_error
        elif base_error:
            next_error = f"{base_error}; {marker}"[:1000]
        else:
            next_error = marker

        row.status = "failed"
        row.progress = max(0, min(99, _safe_int(getattr(row, "progress", 0), 0)))
        row.finished_at = now_dt
        row.error_message = next_error
        row.save(update_fields=["status", "progress", "finished_at", "error_message", "updated_at"])
        stale_count += 1
    return stale_count


def _reconcile_stale_pipeline_state(*, now_dt, runtime_config: dict[str, Any] | None = None) -> dict[str, int]:
    repaired_runs = _mark_stale_daily_runs(now_dt=now_dt, runtime_config=runtime_config)
    repaired_tasks = _mark_stale_crawler_tasks(now_dt=now_dt, runtime_config=runtime_config)
    if repaired_runs or repaired_tasks:
        logger.warning(
            "ops_gateway reconciled stale pipeline state: daily_runs=%s crawler_tasks=%s",
            repaired_runs,
            repaired_tasks,
        )
    return {"daily_runs": repaired_runs, "crawler_tasks": repaired_tasks}


def _trim_checkpoint_value(value: Any, *, max_depth: int = 2):
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        return value[:200]
    if max_depth <= 0:
        return str(value)[:200]
    if isinstance(value, dict):
        trimmed: dict[str, Any] = {}
        for index, (raw_key, raw_value) in enumerate(value.items()):
            if index >= 12:
                break
            key = str(raw_key)[:80]
            trimmed[key] = _trim_checkpoint_value(raw_value, max_depth=max_depth - 1)
        return trimmed
    if isinstance(value, (list, tuple, set)):
        return [_trim_checkpoint_value(item, max_depth=max_depth - 1) for item in list(value)[:8]]
    return str(value)[:200]


def _compact_daily_result_for_summary(result: dict[str, Any]) -> dict[str, Any]:
    compact = _trim_checkpoint_value(result, max_depth=3)
    if not isinstance(compact, dict):
        compact = {}

    checkpoints = result.get("checkpoints")
    if isinstance(checkpoints, list):
        compact["checkpoints"] = [
            _trim_checkpoint_value(item, max_depth=2)
            for item in checkpoints[-80:]
        ]

    for key in ("status", "generated_at", "failed_count", "run_stage", "stage_updated_at"):
        if key in result:
            compact[key] = _trim_checkpoint_value(result.get(key), max_depth=2)

    section_specs: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "import",
            (
                "status",
                "target_count",
                "created_count",
                "updated_count",
                "failed_count",
            ),
        ),
        (
            "seo_daily",
            (
                "status",
                "target_games",
                "created_tasks",
                "published_count",
                "draft_count",
                "skipped_count",
                "failed_count",
            ),
        ),
        (
            "published_recheck",
            (
                "status",
                "target_count",
                "healthy_count",
                "rewritten_count",
                "archived_count",
                "failed_count",
            ),
        ),
    )

    for section_key, metric_keys in section_specs:
        section = result.get(section_key)
        if not isinstance(section, dict):
            continue
        reduced: dict[str, Any] = {}
        for metric_key in metric_keys:
            if metric_key in section:
                reduced[metric_key] = _trim_checkpoint_value(
                    section.get(metric_key), max_depth=2
                )
        items = section.get("items")
        if isinstance(items, list):
            reduced["item_count"] = len(items)
            reduced["items"] = [
                _trim_checkpoint_value(item, max_depth=2)
                for item in items[:12]
                if isinstance(item, dict)
            ]
        compact[section_key] = reduced

    return compact

def _update_run_checkpoint(
    run_row: DailyRobotRun | None,
    *,
    stage: str,
    detail: dict[str, Any] | None = None,
) -> None:
    if run_row is None:
        return
    try:
        current = run_row.summary if isinstance(run_row.summary, dict) else {}
        checkpoints = current.get("checkpoints")
        if not isinstance(checkpoints, list):
            checkpoints = []
        stage_text = str(stage or "").strip()[:120] or "unknown"
        entry: dict[str, Any] = {"stage": stage_text, "at": timezone.now().isoformat()}
        if isinstance(detail, dict) and detail:
            entry["detail"] = _trim_checkpoint_value(detail)
        checkpoints.append(entry)
        current["status"] = "running"
        current["run_stage"] = stage_text
        current["stage_updated_at"] = entry["at"]
        current["checkpoints"] = checkpoints[-120:]
        run_row.summary = current
        run_row.save(update_fields=["summary", "updated_at"])
    except Exception:
        logger.exception("ops_gateway failed to update run checkpoint stage=%s", stage)


def _persist_run_row(
    run_row: DailyRobotRun | None,
    *,
    update_fields: list[str],
    context: str,
) -> bool:
    if run_row is None:
        return False

    fields = list(dict.fromkeys(str(field) for field in (update_fields or []) if str(field)))
    if "updated_at" not in fields:
        fields.append("updated_at")

    for attempt in range(2):
        try:
            run_row.save(update_fields=fields)
            return True
        except OperationalError:
            logger.warning(
                "ops_gateway run save operational error context=%s attempt=%s run_id=%s",
                context,
                attempt + 1,
                getattr(run_row, "id", None),
            )
            close_old_connections()
            continue
        except Exception:
            logger.exception(
                "ops_gateway run save failed context=%s run_id=%s",
                context,
                getattr(run_row, "id", None),
            )
            break

    try:
        payload: dict[str, Any] = {}
        for field in fields:
            if field == "updated_at":
                payload[field] = timezone.now()
                continue
            payload[field] = getattr(run_row, field)
        updated = DailyRobotRun.objects.filter(pk=run_row.pk).update(**payload)
        if updated:
            return True
    except Exception:
        logger.exception(
            "ops_gateway run fallback update failed context=%s run_id=%s",
            context,
            getattr(run_row, "id", None),
        )
    return False


def _resolve_robot_actor(runtime_config: dict[str, Any] | None = None):
    User = get_user_model()
    username = ""
    if runtime_config:
        username = str(runtime_config.get("actor_username") or "").strip()
    if not username:
        username = str(getattr(settings, "OPS_GATEWAY_AUTORUN_ACTOR", "") or "").strip()

    if username:
        user = User.objects.filter(username=username, is_active=True).order_by("id").first()
        if user:
            return user

    user = User.objects.filter(is_superuser=True, is_active=True).order_by("id").first()
    if user:
        return user

    return User.objects.filter(is_staff=True, is_active=True).order_by("id").first()


def _should_skip_for_management_command() -> bool:
    argv = [str(item or "").lower() for item in sys.argv[1:]]
    blocked = {
        "makemigrations",
        "migrate",
        "collectstatic",
        "check",
        "test",
        "shell",
        "dbshell",
        "createsuperuser",
        "changepassword",
        "loaddata",
        "dumpdata",
    }
    return any(arg in blocked for arg in argv)


def should_start_auto_runner() -> bool:
    if not bool(getattr(settings, "OPS_GATEWAY_AUTORUN_ENABLED", True)):
        return False
    if _should_skip_for_management_command():
        return False

    argv = [str(item or "").lower() for item in sys.argv[1:]]
    if "runserver" in argv and "--noreload" not in argv:
        if os.environ.get("RUN_MAIN") not in {"true", "1"}:
            return False
    return True


def run_due_daily_cycle(*, force: bool = False, trigger_source: str = "scheduler") -> dict[str, Any]:
    now = timezone.now()
    run_date = now.date()
    runtime_config = _load_runtime_daily_config()
    run_key = str(getattr(settings, "OPS_GATEWAY_AUTORUN_RUN_KEY", "daily_full_cycle") or "daily_full_cycle").strip()
    if force:
        run_key = f"{run_key}_manual_{now:%H%M%S}"

    try:
        _reconcile_stale_pipeline_state(now_dt=now, runtime_config=runtime_config)

        if not force:
            if not bool(runtime_config.get("is_enabled", True)):
                return {
                    "status": "skipped_disabled",
                    "source": runtime_config.get("source", "settings"),
                    "now": now.isoformat(),
                }

            daily_hour = max(0, min(23, _safe_int(runtime_config.get("daily_hour"), 4)))
            if now.hour < daily_hour:
                return {
                    "status": "skipped_before_window",
                    "daily_hour": daily_hour,
                    "now": now.isoformat(),
                }

            existed = DailyRobotRun.objects.filter(run_key=run_key, run_date=run_date).first()
            if existed:
                if _is_stale_running(existed, now_dt=now, runtime_config=runtime_config):
                    existed.status = DailyRobotRun.STATUS_FAILED
                    existed.error_message = "stale_running_timeout"
                    existed.finished_at = now
                    _persist_run_row(
                        existed,
                        update_fields=["status", "error_message", "finished_at", "updated_at"],
                        context="precheck_mark_stale",
                    )
                else:
                    return {
                        "status": "already_ran",
                        "run_id": existed.id,
                        "run_date": str(run_date),
                        "run_key": run_key,
                        "result_status": existed.status,
                    }
    except (OperationalError, ProgrammingError) as exc:
        return {"status": "db_not_ready", "error": str(exc)[:220]}

    run_row = DailyRobotRun.objects.filter(run_key=run_key, run_date=run_date).first()
    if run_row and force:
        # Force mode should always create an independent manual run key.
        run_row = None

    if run_row and _is_stale_running(run_row, now_dt=now, runtime_config=runtime_config):
        run_row.status = DailyRobotRun.STATUS_RUNNING
        run_row.trigger_source = str(trigger_source or "scheduler")[:32]
        run_row.summary = {}
        run_row.error_message = ""
        run_row.started_at = now
        run_row.finished_at = None
        _persist_run_row(
            run_row,
            update_fields=[
                "status",
                "trigger_source",
                "summary",
                "error_message",
                "started_at",
                "finished_at",
                "updated_at",
            ],
            context="revive_stale_run",
        )

    if run_row is not None and run_row.status != DailyRobotRun.STATUS_RUNNING:
        run_row.status = DailyRobotRun.STATUS_RUNNING
        run_row.trigger_source = str(trigger_source or "scheduler")[:32]
        run_row.summary = {}
        run_row.error_message = ""
        run_row.started_at = now
        run_row.finished_at = None
        _persist_run_row(
            run_row,
            update_fields=[
                "status",
                "trigger_source",
                "summary",
                "error_message",
                "started_at",
                "finished_at",
                "updated_at",
            ],
            context="reuse_non_running_run",
        )

    if run_row is None:
        try:
            run_row = DailyRobotRun.objects.create(
                run_key=run_key,
                run_date=run_date,
                trigger_source=str(trigger_source or "scheduler")[:32],
                status=DailyRobotRun.STATUS_RUNNING,
            )
        except IntegrityError:
            existed = DailyRobotRun.objects.filter(run_key=run_key, run_date=run_date).first()
            if existed and _is_stale_running(existed, now_dt=now, runtime_config=runtime_config):
                existed.status = DailyRobotRun.STATUS_RUNNING
                existed.trigger_source = str(trigger_source or "scheduler")[:32]
                existed.summary = {}
                existed.error_message = ""
                existed.started_at = now
                existed.finished_at = None
                _persist_run_row(
                    existed,
                    update_fields=[
                        "status",
                        "trigger_source",
                        "summary",
                        "error_message",
                        "started_at",
                        "finished_at",
                        "updated_at",
                    ],
                    context="integrity_revive_existing",
                )
                run_row = existed
            else:
                return {
                    "status": "already_ran",
                    "run_id": getattr(existed, "id", None),
                    "run_date": str(run_date),
                    "run_key": run_key,
                    "result_status": getattr(existed, "status", ""),
                }
        except (OperationalError, ProgrammingError) as exc:
            return {"status": "db_not_ready", "error": str(exc)[:220]}

    try:
        posts_min = max(1, min(200, _safe_int(runtime_config.get("posts_min"), 10)))
        posts_max = max(posts_min, min(200, _safe_int(runtime_config.get("posts_max"), 20)))
        _update_run_checkpoint(
            run_row,
            stage="daily_cycle.started",
            detail={
                "run_key": run_key,
                "trigger_source": str(trigger_source or "scheduler"),
                "config_source": str(runtime_config.get("source", "settings") or "settings"),
            },
        )

        def _progress_callback(stage: str, detail: dict[str, Any] | None = None) -> None:
            _update_run_checkpoint(run_row, stage=stage, detail=detail)

        result = run_daily_robot_full_cycle(
            actor=_resolve_robot_actor(runtime_config=runtime_config),
            import_limit=max(1, min(100, _safe_int(runtime_config.get("import_limit"), 30))),
            limit_games=max(1, min(100, _safe_int(runtime_config.get("limit_games"), 6))),
            posts_min=posts_min,
            posts_max=posts_max,
            max_attempts_per_game=max(1, min(5, _safe_int(runtime_config.get("max_attempts_per_game"), 1))),
            rewrite_limit=max(1, min(5, _safe_int(runtime_config.get("rewrite_limit"), 1))),
            review_threshold=max(1, min(100, _safe_int(runtime_config.get("review_threshold"), 78))),
            recent_days=max(1, min(120, _safe_int(runtime_config.get("recent_days"), 30))),
            publish_status=str(runtime_config.get("publish_status") or "published"),
            publish_now=bool(runtime_config.get("publish_now", True)),
            progress_callback=_progress_callback,
        )
        result_status = str(result.get("status") or "").lower()
        pending_summary = run_row.summary if isinstance(run_row.summary, dict) else {}
        checkpoints = pending_summary.get("checkpoints")
        if isinstance(checkpoints, list) and checkpoints:
            result = dict(result)
            result["run_stage"] = str(pending_summary.get("run_stage") or result.get("run_stage") or "finished")
            result["stage_updated_at"] = str(pending_summary.get("stage_updated_at") or timezone.now().isoformat())
            result["checkpoints"] = checkpoints
        run_row.status = (
            DailyRobotRun.STATUS_COMPLETED
            if result_status == "completed"
            else DailyRobotRun.STATUS_PARTIAL
            if result_status == "partial"
            else DailyRobotRun.STATUS_FAILED
        )
        run_row.summary = _compact_daily_result_for_summary(result)
        run_row.error_message = ""
        run_row.finished_at = timezone.now()
        _persist_run_row(
            run_row,
            update_fields=["status", "summary", "error_message", "finished_at", "updated_at"],
            context="finalize_success",
        )
        output = {
            "status": "ok",
            "run_id": run_row.id,
            "run_date": str(run_date),
            "run_key": run_key,
            "config_source": runtime_config.get("source", "settings"),
            "result": result,
        }
        notify_success = bool(getattr(settings, "FEISHU_OPS_NOTIFY_SUCCESS", False))
        if run_row.status in {DailyRobotRun.STATUS_FAILED, DailyRobotRun.STATUS_PARTIAL} or notify_success:
            _notify_daily_result_webhooks(run_row=run_row, payload=output)
        return output
    except Exception as exc:
        run_row.status = DailyRobotRun.STATUS_FAILED
        summary = run_row.summary if isinstance(run_row.summary, dict) else {}
        summary["status"] = DailyRobotRun.STATUS_FAILED
        summary["run_stage"] = str(summary.get("run_stage") or "daily_cycle.exception")
        summary["failed_at"] = timezone.now().isoformat()
        summary["error"] = str(exc)[:1000]
        run_row.summary = summary
        run_row.error_message = str(exc)[:2000]
        run_row.finished_at = timezone.now()
        persisted = _persist_run_row(
            run_row,
            update_fields=["status", "summary", "error_message", "finished_at", "updated_at"],
            context="finalize_exception",
        )
        if not persisted:
            logger.error(
                "ops_gateway could not persist failed run state run_id=%s run_key=%s",
                getattr(run_row, "id", None),
                run_key,
            )
        logger.exception("ops_gateway auto daily cycle failed")
        output = {
            "status": "failed",
            "run_id": run_row.id,
            "run_date": str(run_date),
            "run_key": run_key,
            "error": str(exc),
        }
        _notify_daily_result_webhooks(run_row=run_row, payload=output)
        return output


def _runner_loop() -> None:
    while not _STOP_EVENT.is_set():
        try:
            refresh_bahamut_board_rankings(force=False, trigger_source="scheduler")
        except Exception:
            logger.exception("ops_gateway bahamut ranking auto refresh unexpected error")
        try:
            run_due_daily_cycle(force=False, trigger_source="scheduler")
        except Exception:
            logger.exception("ops_gateway runner loop unexpected error")
        runtime_config = _load_runtime_daily_config()
        interval = max(60, _safe_int(runtime_config.get("poll_seconds"), 900))
        _STOP_EVENT.wait(interval)


def start_auto_runner() -> None:
    global _RUNNER_THREAD
    if not should_start_auto_runner():
        return

    with _RUNNER_LOCK:
        if _RUNNER_THREAD is not None and _RUNNER_THREAD.is_alive():
            return
        _STOP_EVENT.clear()
        _RUNNER_THREAD = threading.Thread(
            target=_runner_loop,
            name="ops-gateway-daily-runner",
            daemon=True,
        )
        _RUNNER_THREAD.start()
        logger.info("ops_gateway daily auto runner started")


def run_daily_cycle_now(*, force: bool = False, trigger_source: str = "manual") -> dict[str, Any]:
    return run_due_daily_cycle(force=force, trigger_source=trigger_source)
