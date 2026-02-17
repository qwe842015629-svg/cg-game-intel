from __future__ import annotations

import concurrent.futures
import html
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import feedparser
import requests


@dataclass(frozen=True)
class SourceTask:
    key: str
    url: str
    parser_type: str  # "json" | "rss"


class GameIntelEngine:
    """
    Concurrent multi-source game intel aggregator.
    Outputs normalized payload to `game_hub.json`.
    """

    def __init__(self, output_path: str | None = None) -> None:
        self.meta_keyword_weights: dict[str, int] = {
            "tier list": 4,
            "meta": 3,
            "build": 3,
            "guide": 2,
            "best": 1,
            "reroll": 2,
            "codes": 1,
        }

        self.output_path = self._resolve_output_path(output_path)
        self.legacy_source = Path("frontend/public/data/games_sync.json")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/130.0.0.0 Safari/537.36"
                )
            }
        )
        self.timeout = 15

        # Prefer alias by stable id when upstream text quality is unstable.
        self.title_alias: dict[str, str] = {
            "com.gameloft.android.ANMP.Gloft5DHM": "Dungeon Hunter 5",
            "com.blizzard.diablo.immortal": "Diablo Immortal",
            "com.mover.twjxsj": "New Swordsman World",
            "com.newtypegames.dl2hmt": "Dynasty Warriors 2",
            "com.miHoYo.GenshinImpact": "Genshin Impact",
            "com.netmarble.bnsmasia": "Blade and Soul Revolution",
            "com.ea.game.pvz2_row": "Plants vs. Zombies 2",
            "com.ChillyRoom.DungeonShooter": "Soul Knight",
            "com.levelinfinite.sgameGlobal": "Honor of Kings",
            "com.activision.callofduty.shooter": "Call of Duty: Mobile",
            "com.netease.g108na": "Destiny: Rising",
            "com.pubg.newstate": "NEW STATE MOBILE",
            "com.gaijingames.wtm": "War Thunder Mobile",
            "com.fingersoft.hillclimb": "Hill Climb Racing",
            "com.gameloft.android.ANMP.GloftA8HM": "Asphalt 8",
            "com.kiloo.subwaysurf": "Subway Surfers",
        }

        self.genre_alias: dict[str, str] = {
            "role playing": "Role Playing",
            "roleplaying": "Role Playing",
            "action": "Action",
            "adventure": "Adventure",
            "strategy": "Strategy",
            "casual": "Casual",
            "shooter": "Shooter",
            "racing": "Racing",
            "puzzle": "Puzzle",
            # Common mojibake values seen in legacy files
            "瑙掕壊鎵紨": "Role Playing",
            "鍔ㄤ綔": "Action",
            "鍐掗櫓": "Adventure",
            "绛栫暐": "Strategy",
            "浼戦棽": "Casual",
            "灏勫嚮": "Shooter",
        }

        self.mojibake_tokens = (
            "�",
            "鈻",
            "锛",
            "銆",
            "鍏",
            "娓",
            "娆",
            "涓滃",
            "閳",
            "閿",
            "濞",
            "鏂",
            "瑙掕壊",
            "鍔ㄤ綔",
            "鍐掗櫓",
            "绛栫暐",
            "浼戦棽",
        )

    def _resolve_output_path(self, output_path: str | None) -> Path:
        if output_path:
            return Path(output_path)

        env_path = os.environ.get("GAME_HUB_OUTPUT")
        if env_path:
            return Path(env_path)

        frontend_public = Path("frontend/public/data")
        if frontend_public.exists():
            return frontend_public / "game_hub.json"
        return Path("public/data/game_hub.json")

    def _tasks(self) -> list[SourceTask]:
        return [
            SourceTask(
                key="app_cn",
                url="https://rss.marketingtools.apple.com/api/v2/cn/apps/top-free/15/games.json",
                parser_type="json",
            ),
            SourceTask(
                key="app_us",
                url="https://rss.marketingtools.apple.com/api/v2/us/apps/top-free/15/games.json",
                parser_type="json",
            ),
            SourceTask(
                key="app_jp",
                url="https://rss.marketingtools.apple.com/api/v2/jp/apps/top-free/15/games.json",
                parser_type="json",
            ),
            SourceTask(
                key="servers",
                url="https://www.freetogame.com/api/games?platform=mobile&sort-by=release-date",
                parser_type="json",
            ),
            SourceTask(
                key="kotaku",
                url="https://kotaku.com/game-tips/rss",
                parser_type="rss",
            ),
            SourceTask(
                key="wiki",
                url="https://genshin-impact.fandom.com/wiki/Special:NewPages?feed=rss",
                parser_type="rss",
            ),
        ]

    def fetch_source(self, task: SourceTask) -> Any | None:
        try:
            response = self.session.get(task.url, timeout=self.timeout)
            response.raise_for_status()
            if task.parser_type == "json":
                return response.json()
            return feedparser.parse(response.content)
        except Exception as exc:
            print(f"[WARN] fetch failed ({task.key}): {exc}")
            return None

    def process_data(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        tasks = self._tasks()

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            future_map = {
                executor.submit(self.fetch_source, task): task.key for task in tasks
            }
            for future in concurrent.futures.as_completed(future_map):
                key = future_map[future]
                try:
                    results[key] = future.result()
                except Exception as exc:
                    print(f"[WARN] unexpected error ({key}): {exc}")
                    results[key] = None

        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "rankings": {
                "CN": self._clean_app_store(results.get("app_cn")),
                "US": self._clean_app_store(results.get("app_us")),
                "JP": self._clean_app_store(results.get("app_jp")),
            },
            "new_releases": self._clean_servers(results.get("servers")),
            "strategies": self._clean_rss(results.get("kotaku"), source="Kotaku", limit=14),
            "wiki_radar": self._clean_rss(results.get("wiki"), source="Genshin Wiki", limit=20),
        }

        fallback_payload = self._load_fallback_payload()
        payload = self._merge_with_fallback(payload, fallback_payload)
        payload["rankings"] = self._apply_global_hot(payload["rankings"])
        payload["stats"] = self._build_stats(payload)

        self._write_payload(payload)
        print(f"[OK] game hub synced -> {self.output_path}")
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _build_stats(self, payload: dict[str, Any]) -> dict[str, Any]:
        rankings = payload.get("rankings", {})
        top_regions = {region: len(items) for region, items in rankings.items()}
        high_value_count = sum(
            1 for item in payload.get("strategies", []) if item.get("is_high_value")
        )
        global_hot_count = sum(
            1
            for region_items in rankings.values()
            for game in region_items
            if game.get("global_hot")
        )
        return {
            "ranking_regions": top_regions,
            "new_release_count": len(payload.get("new_releases", [])),
            "strategy_count": len(payload.get("strategies", [])),
            "wiki_count": len(payload.get("wiki_radar", [])),
            "high_value_strategies": high_value_count,
            "global_hot_entries": global_hot_count,
        }

    def _clean_app_store(self, data: Any) -> list[dict[str, Any]]:
        if not isinstance(data, dict):
            return []

        entries = data.get("feed", {}).get("results", [])
        cleaned: list[dict[str, Any]] = []
        for idx, item in enumerate(entries[:15]):
            app_id = str(item.get("id") or item.get("bundleId") or f"app-{idx + 1}")
            raw_genre = (item.get("genres") or [{}])[0].get("name", "Game")
            cleaned.append(
                {
                    "id": app_id,
                    "rank": idx + 1,
                    "title": self._normalize_title(item.get("name"), app_id, f"app-{idx + 1}"),
                    "icon": item.get("artworkUrl100")
                    or item.get("artworkUrl60")
                    or item.get("artworkUrl512")
                    or "",
                    "author": self._normalize_author(item.get("artistName", "Unknown")),
                    "url": self._safe_text(item.get("url", "")),
                    "genre": self._normalize_genre(raw_genre),
                    "global_hot": False,
                    "global_hot_regions": [],
                }
            )
        return cleaned

    def _clean_servers(self, data: Any) -> list[dict[str, Any]]:
        if not isinstance(data, list):
            return []

        cleaned: list[dict[str, Any]] = []
        for item in data[:20]:
            game_id = str(item.get("id") or "")
            cleaned.append(
                {
                    "id": game_id or f"release-{len(cleaned) + 1}",
                    "title": self._normalize_title(item.get("title"), game_id, "new-release"),
                    "thumbnail": self._safe_text(item.get("thumbnail", "")),
                    "genre": self._normalize_genre(item.get("genre", "Game")),
                    "platform": self._safe_text(item.get("platform", "mobile")),
                    "publisher": self._normalize_author(item.get("publisher", "Unknown")),
                    "release_date": self._safe_text(item.get("release_date", "")),
                    "game_url": self._safe_text(
                        item.get("game_url") or item.get("freetogame_profile_url") or ""
                    ),
                }
            )
        return cleaned

    def _clean_rss(self, feed: Any, *, source: str, limit: int) -> list[dict[str, Any]]:
        if not feed:
            return []
        entries = getattr(feed, "entries", []) or []

        cleaned: list[dict[str, Any]] = []
        for entry in entries[:limit]:
            title = self._safe_text(self._entry(entry, "title", "Untitled"))
            summary = self._strip_html(
                self._entry(entry, "summary", "") or self._entry(entry, "description", "")
            )
            score = self._keyword_weight(f"{title} {summary}")
            cleaned.append(
                {
                    "title": title,
                    "link": self._safe_text(self._entry(entry, "link", "")),
                    "is_high_value": score >= 3,
                    "weight_score": score,
                    "time": self._safe_text(self._entry(entry, "published", ""))
                    or self._safe_text(self._entry(entry, "updated", "")),
                    "source": source,
                }
            )
        return cleaned

    def _entry(self, entry: Any, key: str, default: str = "") -> str:
        if isinstance(entry, dict):
            return str(entry.get(key, default))
        return str(getattr(entry, key, default))

    def _keyword_weight(self, text: str) -> int:
        lower_text = text.lower()
        score = 0
        for keyword, weight in self.meta_keyword_weights.items():
            if keyword in lower_text:
                score += weight
        return score

    def _normalize_title(self, title: Any, game_id: str, fallback: str) -> str:
        if game_id in self.title_alias:
            return self.title_alias[game_id]

        normalized = self._normalize_common_text(self._safe_text(title))
        if not normalized:
            return fallback
        if self._looks_mojibake(normalized):
            return self._title_from_id(game_id) or fallback
        return normalized

    def _normalize_genre(self, genre: Any) -> str:
        raw = self._normalize_common_text(self._safe_text(genre))
        if not raw:
            return "Game"
        lookup = raw.lower()
        if lookup in self.genre_alias:
            return self.genre_alias[lookup]
        if raw in self.genre_alias:
            return self.genre_alias[raw]
        # If upstream genre is non-ASCII and no alias matched, treat as unknown.
        if not re.search(r"[A-Za-z]", raw):
            return "Game"
        if self._looks_mojibake(raw):
            return "Game"
        return raw

    def _normalize_author(self, author: Any) -> str:
        raw = self._normalize_common_text(self._safe_text(author))
        if not raw:
            return "Unknown"
        if self._looks_mojibake(raw):
            return "Unknown"
        return raw

    def _normalize_common_text(self, value: str) -> str:
        if not value:
            return ""
        fixed = value
        replacements = {
            "鈩": "",
            "™": "",
            "®": "",
            "©": "",
            "锛": " ",
            "銆": " ",
            "路": " ",
            "鈥": "'",
            "鈻": " ",
        }
        for old, new in replacements.items():
            fixed = fixed.replace(old, new)
        fixed = re.sub(r"\s+", " ", fixed).strip()
        return fixed

    def _looks_mojibake(self, value: str) -> bool:
        if not value:
            return False
        if "�" in value:
            return True
        if any(token in value for token in self.mojibake_tokens):
            return True
        weird_chars = set("鈻锛銆鍏娓娆閳閿濞")
        weird_count = sum(1 for ch in value if ch in weird_chars)
        return weird_count >= 2 and (weird_count / max(len(value), 1)) > 0.12

    def _title_from_id(self, game_id: str) -> str:
        if not game_id:
            return ""
        tail = game_id.split(".")[-1]
        tail = re.sub(r"([a-z])([A-Z])", r"\1 \2", tail)
        tail = tail.replace("_", " ").replace("-", " ")
        return re.sub(r"\s+", " ", tail).strip()

    def _safe_text(self, value: Any) -> str:
        text = html.unescape(str(value or ""))
        text = text.replace("\u200b", "").replace("\ufeff", "")
        return re.sub(r"\s+", " ", text).strip()

    def _strip_html(self, value: str) -> str:
        return self._safe_text(re.sub(r"<[^>]+>", "", value))

    def _apply_global_hot(self, rankings: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
        title_regions: dict[str, set[str]] = defaultdict(set)
        for region, items in rankings.items():
            for item in items:
                normalized = self._normalize_compare_title(item.get("title", ""))
                if normalized:
                    title_regions[normalized].add(region)

        for items in rankings.values():
            for item in items:
                normalized = self._normalize_compare_title(item.get("title", ""))
                regions = sorted(title_regions.get(normalized, set()))
                item["global_hot"] = bool(item.get("global_hot") or len(regions) >= 2)
                item["global_hot_regions"] = regions
        return rankings

    def _normalize_compare_title(self, title: str) -> str:
        return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", self._safe_text(title).lower())

    def _fallback_empty(self) -> dict[str, Any]:
        return {
            "rankings": {"CN": [], "US": [], "JP": []},
            "new_releases": [],
            "strategies": [],
            "wiki_radar": [],
        }

    def _load_fallback_payload(self) -> dict[str, Any]:
        if not self.legacy_source.exists():
            return self._fallback_empty()

        try:
            with self.legacy_source.open("r", encoding="utf-8") as handle:
                legacy = json.load(handle)
        except Exception as exc:
            print(f"[WARN] fallback load failed: {exc}")
            return self._fallback_empty()

        region_map = {"CN": "hktw", "US": "us", "JP": "sea"}
        rankings: dict[str, list[dict[str, Any]]] = {"CN": [], "US": [], "JP": []}

        for region, old_region in region_map.items():
            old_list = legacy.get("new_releases", {}).get(old_region, [])[:15]
            rows: list[dict[str, Any]] = []
            for idx, game in enumerate(old_list):
                game_id = str(game.get("id") or f"{region}-{idx + 1}")
                rows.append(
                    {
                        "id": game_id,
                        "rank": idx + 1,
                        "title": self._normalize_title(game.get("title"), game_id, f"{region}-{idx + 1}"),
                        "icon": self._safe_text(game.get("icon") or game.get("thumbnail") or ""),
                        "author": self._normalize_author(game.get("publisher") or game.get("developer") or "Unknown"),
                        "url": self._safe_text(game.get("game_url") or ""),
                        "genre": self._normalize_genre(game.get("genre", "Game")),
                        "global_hot": False,
                        "global_hot_regions": [],
                    }
                )
            rankings[region] = rows

        new_releases: list[dict[str, Any]] = []
        merged_source = (
            legacy.get("new_releases", {}).get("hktw", [])[:8]
            + legacy.get("new_releases", {}).get("us", [])[:8]
            + legacy.get("new_releases", {}).get("sea", [])[:8]
        )
        for game in merged_source[:20]:
            game_id = str(game.get("id") or "")
            new_releases.append(
                {
                    "id": game_id or f"release-{len(new_releases) + 1}",
                    "title": self._normalize_title(game.get("title"), game_id, "new-release"),
                    "thumbnail": self._safe_text(game.get("thumbnail") or game.get("icon") or ""),
                    "genre": self._normalize_genre(game.get("genre", "Game")),
                    "platform": self._safe_text(game.get("platform", "mobile")),
                    "publisher": self._normalize_author(game.get("publisher", "Unknown")),
                    "release_date": self._safe_text(game.get("release_date", "")),
                    "game_url": self._safe_text(game.get("game_url") or ""),
                }
            )

        strategies: list[dict[str, Any]] = []
        for game in legacy.get("hot_games", [])[:14]:
            game_id = str(game.get("id") or "")
            title = self._normalize_title(game.get("title"), game_id, "Game")
            guide_title = f"{title} Tier List Build Guide"
            score = self._keyword_weight(guide_title)
            strategies.append(
                {
                    "title": guide_title,
                    "link": f"https://www.google.com/search?q={quote_plus(title)}+Tier+List+Build+Guide",
                    "is_high_value": score >= 3,
                    "weight_score": score,
                    "time": datetime.now(timezone.utc).isoformat(),
                    "source": "LegacyHub",
                }
            )

        wiki_radar = [
            {
                "title": "Genshin Wiki: New pages monitor",
                "link": "https://genshin-impact.fandom.com/wiki/Special:NewPages",
                "is_high_value": False,
                "weight_score": 0,
                "time": datetime.now(timezone.utc).isoformat(),
                "source": "Fallback",
            },
            {
                "title": "Genshin Wiki: Event update monitor",
                "link": "https://genshin-impact.fandom.com/wiki/Special:NewPages",
                "is_high_value": False,
                "weight_score": 0,
                "time": datetime.now(timezone.utc).isoformat(),
                "source": "Fallback",
            },
        ]

        return {
            "rankings": rankings,
            "new_releases": new_releases,
            "strategies": strategies,
            "wiki_radar": wiki_radar,
        }

    def _merge_with_fallback(self, payload: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
        ranking_payload = payload.get("rankings", {})
        fallback_rankings = fallback.get("rankings", {})
        merged_rankings: dict[str, list[dict[str, Any]]] = {}

        for region in ("CN", "US", "JP"):
            region_data = ranking_payload.get(region, []) if isinstance(ranking_payload, dict) else []
            if not region_data:
                region_data = fallback_rankings.get(region, [])
            merged_rankings[region] = region_data

        payload["rankings"] = merged_rankings
        if not payload.get("new_releases"):
            payload["new_releases"] = fallback.get("new_releases", [])
        if not payload.get("strategies"):
            payload["strategies"] = fallback.get("strategies", [])
        if not payload.get("wiki_radar"):
            payload["wiki_radar"] = fallback.get("wiki_radar", [])
        return payload


if __name__ == "__main__":
    engine = GameIntelEngine()
    engine.process_data()
