from __future__ import annotations

import re
from collections.abc import Iterable
from difflib import SequenceMatcher
from typing import Any

import requests
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import BahamutBoardRankingEntry, BahamutBoardRankingSnapshot


RANK_SOURCE_BASE_URL = "http://forum.gamer.com.tw/"
JINA_PROXY_PREFIX = "https://r.jina.ai/"

_REQUEST_TIMEOUT = 30
_MAX_FETCH_PAGES = 24

_RANK_LINE_RE = re.compile(r"^\d{1,4}$")
_BOARD_LINK_RE = re.compile(
    r"\[!\[Image\s+\d+:\s*(?P<title>.*?)\]\([^)]*\)\]\((?P<url>https?://forum\.gamer\.com\.tw/B\.php\?bsn=(?P<bsn>\d+)[^)]*)\)",
    flags=re.I,
)
_NUMERIC_TOKEN_RE = re.compile(r"\d[\d,.]*(?:\.\d+)?")

# 非游戏板块关键词（用于过滤）
_NON_GAME_HINTS = (
    "场外休憩区",
    "場外休憩區",
    "智慧型手機",
    "手机与通讯",
    "手機與通訊",
    "電腦應用綜合討論",
    "电脑应用综合讨论",
    "軟體應用",
    "硬體",
    "动漫",
    "動漫",
    "動漫相關綜合",
    "動畫",
    "漫画",
    "漫畫",
    "小說",
    "轻小说",
    "布袋戏",
    "影視",
    "电影",
    "電視",
    "时尚",
    "時尚",
    "旅游",
    "旅遊",
    "美食",
    "摄影",
    "攝影",
    "理财",
    "理財",
    "政治",
    "校園",
    "汽机车",
    "汽機車",
    "宠物",
    "寵物",
    "站務",
    "二手",
    "公仔",
    "模型",
    "周邊",
    "同人",
)

# 游戏板块关键词（命中则优先保留）
_GAME_HINTS = (
    "游戏",
    "遊戲",
    "手游",
    "手遊",
    "online",
    "rpg",
    "mmorpg",
    "moba",
    "fps",
    "steam",
    "switch",
    "xbox",
    "ps5",
    "playstation",
    "任天堂",
    "宝可梦",
    "寶可夢",
    "pokemon",
    "fate",
    "final fantasy",
    "英雄联盟",
    "英雄聯盟",
    "原神",
    "崩坏",
    "崩壞",
    "鸣潮",
    "鳴潮",
    "明日方舟",
    "魔物猎人",
    "魔物獵人",
    "暗黑",
    "minecraft",
    "valorant",
    "apex",
    "cs2",
    "pubg",
)

_DAILY_RANK_UP_THRESHOLD = 10
_DAILY_HIGH_RANK_THRESHOLD = 50
_DAILY_HOT_PERCENTILE = 0.80


def _build_jina_proxy_url(raw_url: str) -> str:
    return f"{JINA_PROXY_PREFIX}{raw_url}"


def _clean_line(value: str) -> str:
    return str(value or "").replace("\u3000", " ").strip()


def _extract_heat_info(raw_line: str) -> tuple[str, int, int]:
    line = _clean_line(raw_line)
    if not line:
        return "", 0, 0

    numeric_values: list[int] = []
    for match in _NUMERIC_TOKEN_RE.finditer(line):
        token = match.group(0)
        try:
            value = float(token.replace(",", ""))
        except Exception:
            continue
        unit = line[match.end() : match.end() + 1]
        if unit in {"万", "萬"}:
            value *= 10000
        numeric_values.append(int(round(value)))

    if not numeric_values:
        return line, 0, 0

    heat_value = max(numeric_values)
    activity_value = numeric_values[-1] if len(numeric_values) >= 2 else 0
    return line, max(0, heat_value), max(0, activity_value)


def _looks_like_game_title(title: str) -> bool:
    text = _clean_line(title)
    if not text:
        return False

    lowered = text.lower()
    if any(hint.lower() in lowered for hint in _GAME_HINTS):
        return True
    if any(hint.lower() in lowered for hint in _NON_GAME_HINTS):
        return False
    return True


def _parse_rank_page(markdown_text: str) -> list[dict[str, Any]]:
    lines = [_clean_line(line) for line in (markdown_text or "").splitlines()]
    rows: list[dict[str, Any]] = []

    for idx, line in enumerate(lines):
        if "B.php?bsn=" not in line:
            continue
        link_match = _BOARD_LINK_RE.search(line)
        if not link_match:
            continue

        rank = 0
        for back in range(idx - 1, max(-1, idx - 8), -1):
            if _RANK_LINE_RE.match(lines[back]):
                try:
                    rank = int(lines[back])
                except Exception:
                    rank = 0
                break
        if rank <= 0:
            continue

        heat_line = ""
        for fwd in range(idx + 1, min(len(lines), idx + 10)):
            candidate = lines[fwd]
            if not candidate:
                continue
            if _RANK_LINE_RE.match(candidate):
                break
            if "B.php?bsn=" in candidate:
                break
            candidate_lower = candidate.lower()
            if candidate.startswith("![Image") or "img_crown" in candidate_lower or "rank" in candidate_lower:
                continue
            if any(ch.isdigit() for ch in candidate):
                heat_line = candidate
                break

        heat_text, heat_value, activity_value = _extract_heat_info(heat_line)
        rows.append(
            {
                "rank": rank,
                "board_title": _clean_line(link_match.group("title")),
                "board_url": _clean_line(link_match.group("url")),
                "bsn": int(link_match.group("bsn")),
                "heat_text": heat_text,
                "heat_value": heat_value,
                "activity_value": activity_value,
            }
        )

    rows.sort(key=lambda item: (int(item.get("rank") or 0), int(item.get("bsn") or 0)))
    return rows


def _fetch_page_rank_rows(*, page: int) -> tuple[list[dict[str, Any]], str]:
    source_url = f"{RANK_SOURCE_BASE_URL}?page={page}"
    proxy_url = _build_jina_proxy_url(source_url)
    response = requests.get(
        proxy_url,
        timeout=_REQUEST_TIMEOUT,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/plain,text/markdown;q=0.9,*/*;q=0.8",
        },
    )
    response.raise_for_status()
    response.encoding = "utf-8"
    markdown_text = response.text or ""
    rows = _parse_rank_page(markdown_text=markdown_text)
    return rows, source_url


def _pick_heat_threshold(values: Iterable[int]) -> int:
    clean_values = sorted(int(v) for v in values if int(v) > 0)
    if not clean_values:
        return 0
    idx = int(len(clean_values) * _DAILY_HOT_PERCENTILE) - 1
    idx = max(0, min(len(clean_values) - 1, idx))
    return clean_values[idx]


def _latest_previous_snapshot(today) -> BahamutBoardRankingSnapshot | None:
    return (
        BahamutBoardRankingSnapshot.objects.filter(snapshot_date__lt=today, status__in=["completed", "partial"])
        .order_by("-snapshot_date", "-id")
        .first()
    )


def _snapshot_rank_map(snapshot: BahamutBoardRankingSnapshot | None) -> dict[int, int]:
    if snapshot is None:
        return {}
    rows = snapshot.entries.values("bsn", "rank")
    data: dict[int, int] = {}
    for row in rows:
        bsn = int(row.get("bsn") or 0)
        rank = int(row.get("rank") or 0)
        if bsn > 0 and rank > 0:
            data[bsn] = rank
    return data


def refresh_bahamut_board_rankings(
    *,
    force: bool = False,
    trigger_source: str = "scheduler",
    target_game_count: int = 200,
    max_pages: int = _MAX_FETCH_PAGES,
) -> dict[str, Any]:
    now = timezone.now()
    today = now.date()
    target_count = max(20, min(300, int(target_game_count or 200)))
    max_pages = max(1, min(80, int(max_pages or _MAX_FETCH_PAGES)))

    snapshot = BahamutBoardRankingSnapshot.objects.filter(snapshot_date=today).first()
    if snapshot and not force and snapshot.status in {"completed", "partial"} and snapshot.game_count >= target_count:
        return {
            "status": "already_updated",
            "snapshot_id": snapshot.id,
            "snapshot_date": str(snapshot.snapshot_date),
            "game_count": snapshot.game_count,
            "summary": snapshot.summary if isinstance(snapshot.summary, dict) else {},
        }

    if snapshot is None:
        created = False
        try:
            snapshot, created = BahamutBoardRankingSnapshot.objects.get_or_create(
                snapshot_date=today,
                defaults={
                    "trigger_source": str(trigger_source or "scheduler")[:32],
                    "status": BahamutBoardRankingSnapshot.STATUS_RUNNING,
                    "source_url": RANK_SOURCE_BASE_URL,
                    "summary": {},
                },
            )
        except IntegrityError:
            snapshot = BahamutBoardRankingSnapshot.objects.filter(snapshot_date=today).first()
            if snapshot is None:
                raise
        if snapshot and not created and not force and snapshot.status in {"completed", "partial"} and snapshot.game_count >= target_count:
            return {
                "status": "already_updated",
                "snapshot_id": snapshot.id,
                "snapshot_date": str(snapshot.snapshot_date),
                "game_count": snapshot.game_count,
                "summary": snapshot.summary if isinstance(snapshot.summary, dict) else {},
            }
    else:
        snapshot.trigger_source = str(trigger_source or "scheduler")[:32]
        snapshot.status = BahamutBoardRankingSnapshot.STATUS_RUNNING
        snapshot.error_message = ""
        snapshot.total_raw_count = 0
        snapshot.game_count = 0
        snapshot.summary = {}
        snapshot.started_at = now
        snapshot.finished_at = None
        snapshot.save(
            update_fields=[
                "trigger_source",
                "status",
                "error_message",
                "total_raw_count",
                "game_count",
                "summary",
                "started_at",
                "finished_at",
                "updated_at",
            ]
        )

    if snapshot and snapshot.status != BahamutBoardRankingSnapshot.STATUS_RUNNING:
        snapshot.trigger_source = str(trigger_source or "scheduler")[:32]
        snapshot.status = BahamutBoardRankingSnapshot.STATUS_RUNNING
        snapshot.error_message = ""
        snapshot.total_raw_count = 0
        snapshot.game_count = 0
        snapshot.summary = {}
        snapshot.started_at = now
        snapshot.finished_at = None
        snapshot.save(
            update_fields=[
                "trigger_source",
                "status",
                "error_message",
                "total_raw_count",
                "game_count",
                "summary",
                "started_at",
                "finished_at",
                "updated_at",
            ]
        )

    fetch_errors: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    page_stats: list[dict[str, Any]] = []
    empty_pages = 0

    for page in range(1, max_pages + 1):
        try:
            rows, source_url = _fetch_page_rank_rows(page=page)
        except Exception as exc:
            fetch_errors.append({"page": page, "error": str(exc)[:260]})
            page_stats.append({"page": page, "status": "error", "count": 0})
            continue

        page_stats.append({"page": page, "status": "ok", "count": len(rows), "source_url": source_url})
        if not rows:
            empty_pages += 1
            if empty_pages >= 2 and len(all_rows) >= target_count:
                break
            continue

        empty_pages = 0
        all_rows.extend(rows)

        max_rank = max(int(row.get("rank") or 0) for row in rows)
        if max_rank >= target_count + 50 and len(all_rows) >= target_count:
            break

    dedup_map: dict[int, dict[str, Any]] = {}
    for row in sorted(all_rows, key=lambda item: (int(item.get("rank") or 0), int(item.get("bsn") or 0))):
        bsn = int(row.get("bsn") or 0)
        rank = int(row.get("rank") or 0)
        if bsn <= 0 or rank <= 0:
            continue
        existed = dedup_map.get(bsn)
        if existed is None or rank < int(existed.get("rank") or 0):
            dedup_map[bsn] = row

    ordered_rows = sorted(dedup_map.values(), key=lambda item: int(item.get("rank") or 0))
    game_rows = [row for row in ordered_rows if _looks_like_game_title(str(row.get("board_title") or ""))]
    game_rows = game_rows[:target_count]

    prev_map = _snapshot_rank_map(_latest_previous_snapshot(today))
    heat_threshold = _pick_heat_threshold(row.get("heat_value", 0) for row in game_rows)

    entries_to_create: list[BahamutBoardRankingEntry] = []
    selected_count = 0
    new_count = 0
    rising_count = 0

    for row in game_rows:
        rank = int(row.get("rank") or 0)
        bsn = int(row.get("bsn") or 0)
        previous_rank = prev_map.get(bsn)
        rank_change = int(previous_rank - rank) if previous_rank else 0
        is_new_entry = previous_rank is None
        is_rank_rising = bool(previous_rank and rank_change >= _DAILY_RANK_UP_THRESHOLD)
        is_high_rank = rank > 0 and rank <= _DAILY_HIGH_RANK_THRESHOLD
        heat_value = int(row.get("heat_value") or 0)
        is_hot = heat_threshold > 0 and heat_value >= heat_threshold
        selected_for_daily = bool(is_new_entry or is_rank_rising or is_high_rank or is_hot)

        if selected_for_daily:
            selected_count += 1
        if is_new_entry:
            new_count += 1
        if is_rank_rising:
            rising_count += 1

        entries_to_create.append(
            BahamutBoardRankingEntry(
                snapshot=snapshot,
                rank=rank,
                board_title=str(row.get("board_title") or "")[:255],
                board_url=str(row.get("board_url") or ""),
                bsn=bsn,
                heat_text=str(row.get("heat_text") or "")[:80],
                heat_value=heat_value,
                activity_value=int(row.get("activity_value") or 0),
                is_game=True,
                previous_rank=previous_rank,
                rank_change=rank_change,
                is_new_entry=is_new_entry,
                is_rank_rising=is_rank_rising,
                is_high_rank=is_high_rank,
                is_hot=is_hot,
                selected_for_daily=selected_for_daily,
                raw_payload=row,
            )
        )

    with transaction.atomic():
        BahamutBoardRankingEntry.objects.filter(snapshot=snapshot).delete()
        if entries_to_create:
            BahamutBoardRankingEntry.objects.bulk_create(entries_to_create, batch_size=500)

    status_value = BahamutBoardRankingSnapshot.STATUS_COMPLETED
    if not entries_to_create:
        status_value = BahamutBoardRankingSnapshot.STATUS_FAILED
    elif len(entries_to_create) < target_count:
        status_value = BahamutBoardRankingSnapshot.STATUS_PARTIAL

    summary = {
        "generated_at": timezone.now().isoformat(),
        "target_game_count": target_count,
        "raw_count": len(ordered_rows),
        "game_count": len(entries_to_create),
        "selected_count": selected_count,
        "new_entry_count": new_count,
        "rank_rising_count": rising_count,
        "heat_threshold": heat_threshold,
        "page_stats": page_stats,
        "fetch_errors": fetch_errors,
        "criteria": {
            "rank_up_threshold": _DAILY_RANK_UP_THRESHOLD,
            "high_rank_threshold": _DAILY_HIGH_RANK_THRESHOLD,
            "hot_percentile": _DAILY_HOT_PERCENTILE,
            "or_conditions": ["rank_rising", "hot", "new_entry", "high_rank"],
        },
    }

    snapshot.status = status_value
    snapshot.total_raw_count = len(ordered_rows)
    snapshot.game_count = len(entries_to_create)
    snapshot.summary = summary
    snapshot.error_message = "" if status_value != BahamutBoardRankingSnapshot.STATUS_FAILED else "no_valid_game_rows"
    snapshot.finished_at = timezone.now()
    snapshot.save(
        update_fields=[
            "status",
            "total_raw_count",
            "game_count",
            "summary",
            "error_message",
            "finished_at",
            "updated_at",
        ]
    )

    return {
        "status": status_value,
        "snapshot_id": snapshot.id,
        "snapshot_date": str(snapshot.snapshot_date),
        "raw_count": len(ordered_rows),
        "game_count": len(entries_to_create),
        "selected_count": selected_count,
        "fetch_errors_count": len(fetch_errors),
        "summary": summary,
    }


def get_latest_bahamut_snapshot() -> BahamutBoardRankingSnapshot | None:
    return (
        BahamutBoardRankingSnapshot.objects.filter(status__in=["completed", "partial"])
        .order_by("-snapshot_date", "-id")
        .first()
    )


def _normalize_match_text(value: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text


def resolve_bahamut_bsn_for_game_title(game_title: str) -> dict[str, Any]:
    title = str(game_title or "").strip()
    if not title:
        return {"bsn": None, "board_url": "", "source": "ranking_empty_title", "confidence": 0.0}

    latest = get_latest_bahamut_snapshot()
    if latest is None:
        return {"bsn": None, "board_url": "", "source": "ranking_snapshot_missing", "confidence": 0.0}

    norm_title = _normalize_match_text(title)
    if not norm_title:
        return {"bsn": None, "board_url": "", "source": "ranking_empty_title", "confidence": 0.0}

    entries = list(latest.entries.filter(is_game=True).order_by("rank")[:600])
    best: BahamutBoardRankingEntry | None = None
    best_score = 0.0

    for entry in entries:
        entry_norm = _normalize_match_text(entry.board_title)
        if not entry_norm:
            continue
        if norm_title == entry_norm:
            ratio = 1.0
        elif norm_title in entry_norm or entry_norm in norm_title:
            ratio = 0.94
        else:
            ratio = SequenceMatcher(None, norm_title, entry_norm).ratio()
        if ratio > best_score:
            best_score = ratio
            best = entry

    if best is None or best_score < 0.66:
        return {
            "bsn": None,
            "board_url": "",
            "source": "ranking_no_match",
            "confidence": round(best_score, 4),
        }

    return {
        "bsn": int(best.bsn),
        "board_url": str(best.board_url),
        "source": "bahamut_ranking_cache",
        "confidence": round(best_score, 4),
        "snapshot_date": str(best.snapshot.snapshot_date),
        "rank": int(best.rank),
        "board_title": str(best.board_title),
    }


def select_bahamut_entries_for_daily(*, limit: int = 6) -> list[dict[str, Any]]:
    target = max(1, min(100, int(limit or 6)))
    latest = get_latest_bahamut_snapshot()
    if latest is None:
        return []

    rows = (
        latest.entries.filter(is_game=True, selected_for_daily=True)
        .order_by("rank", "-heat_value", "-rank_change", "id")
        .values(
            "rank",
            "board_title",
            "board_url",
            "bsn",
            "heat_text",
            "heat_value",
            "activity_value",
            "previous_rank",
            "rank_change",
            "is_new_entry",
            "is_rank_rising",
            "is_high_rank",
            "is_hot",
        )[:target]
    )

    results: list[dict[str, Any]] = []
    for row in rows:
        results.append(
            {
                "rank": int(row.get("rank") or 0),
                "board_title": str(row.get("board_title") or ""),
                "board_url": str(row.get("board_url") or ""),
                "bsn": int(row.get("bsn") or 0),
                "heat_text": str(row.get("heat_text") or ""),
                "heat_value": int(row.get("heat_value") or 0),
                "activity_value": int(row.get("activity_value") or 0),
                "previous_rank": int(row.get("previous_rank") or 0) if row.get("previous_rank") else None,
                "rank_change": int(row.get("rank_change") or 0),
                "is_new_entry": bool(row.get("is_new_entry")),
                "is_rank_rising": bool(row.get("is_rank_rising")),
                "is_high_rank": bool(row.get("is_high_rank")),
                "is_hot": bool(row.get("is_hot")),
                "snapshot_date": str(latest.snapshot_date),
                "source": "bahamut_ranking_cache",
            }
        )
    return results


def search_bahamut_entries(*, q: str, limit: int = 60) -> list[dict[str, Any]]:
    latest = get_latest_bahamut_snapshot()
    if latest is None:
        return []

    query = str(q or "").strip()
    if not query:
        rows = latest.entries.filter(is_game=True).order_by("rank")[: max(1, min(200, limit))]
    else:
        rows = (
            latest.entries.filter(is_game=True)
            .filter(board_title__icontains=query)
            .order_by("rank")[: max(1, min(200, limit))]
        )

    return [
        {
            "rank": int(item.rank),
            "board_title": str(item.board_title),
            "board_url": str(item.board_url),
            "bsn": int(item.bsn),
            "heat_text": str(item.heat_text),
            "heat_value": int(item.heat_value),
            "previous_rank": int(item.previous_rank) if item.previous_rank else None,
            "rank_change": int(item.rank_change),
            "is_new_entry": bool(item.is_new_entry),
            "is_rank_rising": bool(item.is_rank_rising),
            "is_high_rank": bool(item.is_high_rank),
            "is_hot": bool(item.is_hot),
            "selected_for_daily": bool(item.selected_for_daily),
            "snapshot_date": str(latest.snapshot_date),
        }
        for item in rows
    ]
