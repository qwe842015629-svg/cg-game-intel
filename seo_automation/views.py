import os
from django.db.models import Q
import hashlib
import mimetypes
import re
import uuid
from typing import Any
from urllib.parse import quote, urlparse
from io import BytesIO

import requests
try:
    from PIL import Image, ImageEnhance
except Exception:  # pragma: no cover
    Image = None
    ImageEnhance = None
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from game_article.models import Article, ArticleCategory, ArticleTag
from game_page.models import GamePage
from main.models import MediaAsset

from .models import CrawlerTask, LLMApiSetting, SeoArticle, SeoKeywordWeight
from .serializers import (
    BahamutTaskRunSerializer,
    CrawlerTaskSerializer,
    LLMApiConnectionTestSerializer,
    LLMApiSettingSerializer,
    SeoArticleSerializer,
    SeoKeywordWeightSerializer,
    SeoRewriteRequestSerializer,
    SeoRewriteResponseSerializer,
)
from .services import (
    BahamutCrawler,
    build_media_gallery_html,
    build_media_items,
    build_meta_fields,
    build_standalone_seo_html_document,
    compose_rich_seo_article_html,
    inject_game_internal_link,
    merge_unique_tags,
    run_step5_quality_enhancement,
    rewrite_bahamut_text,
    sanitize_seo_summary_text,
    test_llm_connection,
)
from .services.quality_enhancement import _filter_quality_image_candidates, _search_bing_images


def _normalize_stop_after_step(value: int | str | None) -> int:
    try:
        step = int(value or 5)
    except Exception:
        step = 5
    return max(1, min(5, step))


def _stage_status_from_count(*, count: int, errors: list[dict] | list[str] | None, pending: bool = False) -> str:
    if pending:
        return "pending"
    if count > 0 and errors:
        return "partial"
    if count > 0:
        return "completed"
    if errors:
        return "failed"
    return "empty"


def _to_int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if not text:
        return default
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _build_operator_summary_payload(
    *,
    task_id: int | None,
    task_status: str,
    result_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = result_payload if isinstance(result_payload, dict) else {}
    pipeline = payload.get("pipeline") if isinstance(payload.get("pipeline"), dict) else {}
    crawl = payload.get("crawl") if isinstance(payload.get("crawl"), dict) else {}
    rewrite = payload.get("rewrite") if isinstance(payload.get("rewrite"), dict) else {}
    quality = payload.get("quality") if isinstance(payload.get("quality"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    stages = crawl.get("stages") if isinstance(crawl.get("stages"), dict) else {}

    stage_rows: list[dict[str, Any]] = []
    for key, label in (
        ("stage1_links", "步骤1 链接抓取"),
        ("stage2_details", "步骤2 内容提取"),
        ("stage3_seo_analysis", "步骤3 SEO分析"),
        ("stage4_seo_generation", "步骤4 文章生成"),
        ("stage5_quality_output", "步骤5 图文优化"),
    ):
        stage_data = stages.get(key) if isinstance(stages.get(key), dict) else {}
        stage_rows.append(
            {
                "key": key,
                "label": label,
                "status": str(stage_data.get("status") or "pending"),
                "count": _to_int(stage_data.get("count")),
                "errors_count": _to_int(stage_data.get("errors_count")),
            }
        )

    issues: list[str] = []
    for item in (rewrite.get("errors") if isinstance(rewrite.get("errors"), list) else [])[:4]:
        text = str(item).strip()
        if text:
            issues.append(f"步骤4：{text}")
    for item in (quality.get("errors") if isinstance(quality.get("errors"), list) else [])[:4]:
        text = str(item).strip()
        if text:
            issues.append(f"步骤5：{text}")
    if not issues:
        issues.append("暂无异常，流程可继续。")

    return {
        "task_id": _to_int(task_id),
        "status": str(task_status or ""),
        "step_completed": _to_int(pipeline.get("step_completed")),
        "metrics": {
            "links_count": _to_int(summary.get("links_count") or crawl.get("links_count")),
            "details_count": _to_int(summary.get("details_count") or crawl.get("details_count")),
            "analysis_count": _to_int(summary.get("analysis_count")),
            "rewrite_count": _to_int(summary.get("rewrite_count") or rewrite.get("rewrite_count")),
            "quality_count": _to_int(summary.get("quality_count") or quality.get("optimized_count")),
            "image_count_step4": _to_int(summary.get("media_count") or rewrite.get("media_count")),
            "image_count_step5": _to_int(summary.get("quality_image_count") or quality.get("image_count")),
        },
        "article_ids": summary.get("article_ids") if isinstance(summary.get("article_ids"), list) else [],
        "stages": stage_rows,
        "issues": issues,
    }


def _attach_operator_summary(
    *,
    task_id: int | None,
    task_status: str,
    result_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = dict(result_payload) if isinstance(result_payload, dict) else {}
    payload["operator_summary"] = _build_operator_summary_payload(
        task_id=task_id,
        task_status=task_status,
        result_payload=payload,
    )
    return payload


def _extract_text_tokens_for_seo(text: str) -> list[str]:
    raw = re.sub(r"<[^>]+>", " ", str(text or ""))
    raw = re.sub(r"\s+", " ", raw).strip().lower()
    tokens = re.findall(r"[a-z0-9\u4e00-\u9fff]{2,20}", raw)
    stop_words = {
        "http",
        "https",
        "www",
        "com",
        "forum",
        "bahamut",
        "gamer",
        "content",
        "title",
        "game",
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "攻略",
        "文章",
        "內容",
        "内容",
        "遊戲",
        "游戏",
    }
    clean_tokens: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token.isdigit():
            continue
        if token in stop_words:
            continue
        if token in seen:
            continue
        seen.add(token)
        clean_tokens.append(token)
    return clean_tokens


def _build_seo_analysis(
    *,
    posts: list[dict[str, Any]],
    payload: dict,
    task: CrawlerTask,
    game: GamePage | None,
) -> dict[str, Any]:
    custom_keywords = [
        str(item).strip()
        for item in (payload.get("custom_keywords") or [])
        if str(item).strip()
    ]

    weighted_rows = list(
        SeoKeywordWeight.objects.filter(is_active=True)
        .order_by("-weight")
        .values("keyword", "weight", "intent", "keyword_group")[:200]
    )

    analysis_items: list[dict[str, Any]] = []
    global_keywords: list[str] = []
    global_seen: set[str] = set()
    default_game_name = game.title if game else (task.keyword or payload.get("keyword") or "游戏")

    for idx, post in enumerate(posts or [], start=1):
        title = str(post.get("title") or "").strip()
        topic_url = str(post.get("topic_url") or "").strip()
        content = str(post.get("content") or "")
        merged_text = "\n".join(filter(None, [title, content, str(post.get("snippet") or "")]))
        lowered = merged_text.lower()

        matched_weighted: list[dict[str, Any]] = []
        for row in weighted_rows:
            keyword = str(row.get("keyword") or "").strip()
            if not keyword:
                continue
            if keyword.lower() in lowered:
                matched_weighted.append(
                    {
                        "keyword": keyword,
                        "weight": float(row.get("weight") or 1),
                        "intent": row.get("intent") or "informational",
                        "group": row.get("keyword_group") or "general",
                    }
                )

        matched_weighted.sort(key=lambda item: item.get("weight", 0), reverse=True)
        candidate_tokens = _extract_text_tokens_for_seo(merged_text)

        focus_keywords = merge_unique_tags(
            base_tags=[item["keyword"] for item in matched_weighted],
            extra_tags=[*custom_keywords, *candidate_tokens[:8]],
            limit=10,
        )
        if not focus_keywords:
            focus_keywords = merge_unique_tags(
                base_tags=[default_game_name],
                extra_tags=custom_keywords,
                limit=6,
            )

        long_tail_seed: list[str] = []
        for kw in focus_keywords[:4]:
            long_tail_seed.append(f"{default_game_name} {kw}")
        for kw in focus_keywords[:2]:
            long_tail_seed.extend([f"{kw} 代储", f"{kw} 充值", f"{kw} 攻略"])

        long_tail_keywords = merge_unique_tags(
            base_tags=long_tail_seed,
            extra_tags=[],
            limit=10,
        )

        summary_text = re.sub(r"\s+", " ", merged_text).strip()[:160]
        search_intent = matched_weighted[0]["intent"] if matched_weighted else "informational"
        outline = [
            "版本重点与玩法变化",
            "角色/阵容与资源规划",
            "充值路径与风险提醒",
            "FAQ 与行动建议",
        ]

        item = {
            "index": idx,
            "topic_url": topic_url,
            "title": title,
            "focus_keywords": focus_keywords,
            "long_tail_keywords": long_tail_keywords,
            "search_intent": search_intent,
            "summary": summary_text,
            "outline": outline,
            "image_count": len(post.get("image_urls") or []),
            "rewrite_keywords": merge_unique_tags(
                base_tags=focus_keywords,
                extra_tags=long_tail_keywords,
                limit=12,
            ),
        }
        analysis_items.append(item)

        for keyword in item["rewrite_keywords"]:
            key = str(keyword).strip().lower()
            if not key or key in global_seen:
                continue
            global_seen.add(key)
            global_keywords.append(str(keyword).strip())

    return {
        "status": "completed" if analysis_items else "empty",
        "generated_at": timezone.now().isoformat(),
        "post_count": len(posts or []),
        "items": analysis_items,
        "global_keywords": global_keywords[:30],
    }


def _is_bahamut_url(url: str) -> bool:
    value = str(url or "").strip()
    if not value:
        return False
    try:
        host = urlparse(value).netloc.lower()
    except Exception:
        return False
    return "forum.gamer.com.tw" in host


def _build_preferred_source_reference(
    *,
    game: GamePage | None,
    game_name: str,
    fallback_title: str = "",
    fallback_url: str = "",
) -> tuple[str, str]:
    normalized_game_name = (game_name or "游戏").strip()
    if game and str(getattr(game, "google_play_id", "") or "").strip():
        package_id = str(game.google_play_id).strip()
        return (
            f"{normalized_game_name} Google Play",
            f"https://play.google.com/store/apps/details?id={quote(package_id, safe='')}",
        )

    if normalized_game_name:
        return (
            f"{normalized_game_name} App Store",
            f"https://apps.apple.com/tw/iphone/search?term={quote(normalized_game_name)}",
        )

    fallback_href = str(fallback_url or "").strip()
    if fallback_href and not _is_bahamut_url(fallback_href):
        return (fallback_title or "参考来源", fallback_href)
    return (fallback_title or "官方应用页面", "")


def _resolve_related_game_by_name(game_name: str) -> GamePage | None:
    keyword = str(game_name or "").strip()
    if not keyword:
        return None

    normalized = re.sub(r"\s+", " ", keyword)
    normalized = re.sub(r"[|｜:：\-—_].*$", "", normalized).strip()
    normalized = re.sub(r"(攻略|教學|教程|心得|懶人包|新手|版本|玩法|儲值|充值|代儲).*$", "", normalized).strip()
    if not normalized:
        normalized = keyword.strip()

    exact = (
        GamePage.objects.filter(
            Q(title__iexact=normalized) | Q(title_tw__iexact=normalized)
        )
        .order_by("-is_hot", "-is_recommended", "-updated_at")
        .first()
    )
    if exact:
        return exact

    if len(normalized) < 2:
        return None

    return (
        GamePage.objects.filter(
            Q(title__icontains=normalized) | Q(title_tw__icontains=normalized)
        )
        .order_by("-is_hot", "-is_recommended", "-updated_at")
        .first()
    )


def _get_analysis_item_for_post(
    *,
    analysis_items: list[dict[str, Any]],
    post: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    topic_url = str(post.get("topic_url") or "").strip()
    if topic_url:
        for item in analysis_items:
            if str(item.get("topic_url") or "").strip() == topic_url:
                return item
    if 0 <= index < len(analysis_items):
        return analysis_items[index]
    return {}


_ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif"}
_COVER_FETCH_CONNECT_TIMEOUT = 4
_COVER_FETCH_READ_TIMEOUT = 8
_COVER_MAX_REMOTE_ATTEMPTS = 12
_COVER_EXTRA_BING_QUERY_COUNT = 3
_COVER_UNIQUE_VARIANT_ATTEMPTS = 8
_MIN_COVER_IMAGE_BYTES = 6 * 1024
_MIN_COVER_WIDTH = 320
_MIN_COVER_HEIGHT = 180
_COVER_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}


def _cover_payload_signature(payload: bytes) -> str:
    if not payload:
        return ""
    return hashlib.md5(payload).hexdigest()


def _dedupe_cover_candidates(candidates: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in candidates:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _extract_cover_candidates_from_article_content(article: Article) -> list[str]:
    candidates: list[str] = []
    for html in (article.content, article.excerpt, article.summary):
        if not html:
            continue
        for item in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', str(html), flags=re.I):
            value = str(item or "").strip()
            if value:
                candidates.append(value)
    return _dedupe_cover_candidates(candidates)


def _guess_image_extension(*, source: str = "", content_type: str = "") -> str:
    parsed = urlparse(source or "")
    path = parsed.path or source
    ext = os.path.splitext(path)[1].lower()
    if ext in _ALLOWED_IMAGE_EXTENSIONS:
        if ext == ".jpe":
            return ".jpg"
        return ext

    mime = (content_type or "").split(";")[0].strip().lower()
    guessed = mimetypes.guess_extension(mime) if mime else ""
    if guessed == ".jpe":
        guessed = ".jpg"
    if guessed in _ALLOWED_IMAGE_EXTENSIONS:
        return guessed
    return ".jpg"


def _is_svg_payload(*, payload: bytes, content_type: str = "", source: str = "") -> bool:
    lowered_type = str(content_type or "").lower()
    lowered_source = str(source or "").lower()
    if "image/svg+xml" in lowered_type or lowered_source.endswith(".svg"):
        return True

    head = bytes(payload[:512]).lstrip().lower() if payload else b""
    if head.startswith(b"<svg") or b"<svg" in head[:220]:
        return True
    if head.startswith(b"<?xml") and b"<svg" in head:
        return True
    return False


def _is_valid_cover_payload(*, payload: bytes, content_type: str = "", source: str = "") -> bool:
    if not payload or len(payload) < _MIN_COVER_IMAGE_BYTES:
        return False
    if _is_svg_payload(payload=payload, content_type=content_type, source=source):
        return False

    if Image is None:
        return True

    try:
        image = Image.open(BytesIO(payload))
        width, height = image.size
    except Exception:
        return False
    if width < _MIN_COVER_WIDTH or height < _MIN_COVER_HEIGHT:
        return False
    return True


def _read_field_file_payload(file_field: Any, *, source_hint: str = "") -> tuple[bytes, str] | None:
    if not file_field:
        return None

    file_name = str(getattr(file_field, "name", "") or "").strip()
    if not file_name:
        return None
    try:
        storage = getattr(file_field, "storage", None)
        if storage is not None and not storage.exists(file_name):
            return None
    except Exception:
        return None

    try:
        with file_field.open("rb") as fh:
            payload = fh.read()
    except Exception:
        return None
    if not payload:
        return None

    content_type = mimetypes.guess_type(file_name)[0] or ""
    source = source_hint or file_name
    if not _is_valid_cover_payload(payload=payload, content_type=content_type, source=source):
        return None
    ext = _guess_image_extension(source=file_name, content_type=content_type)
    return payload, ext


def _read_local_media_bytes(candidate_url: str) -> tuple[bytes, str] | None:
    if not candidate_url:
        return None

    parsed = urlparse(candidate_url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None

    raw_path = parsed.path if parsed.scheme else candidate_url
    raw_path = str(raw_path or "").strip()
    if not raw_path:
        return None

    media_url = str(getattr(settings, "MEDIA_URL", "/media/") or "/media/")
    media_root = str(getattr(settings, "MEDIA_ROOT", "") or "")
    if not media_root:
        return None

    if raw_path.startswith(media_url):
        rel_path = raw_path[len(media_url) :].lstrip("/\\")
    elif raw_path.startswith("/media/"):
        rel_path = raw_path[len("/media/") :].lstrip("/\\")
    else:
        return None

    local_path = os.path.join(media_root, rel_path)
    if not os.path.isfile(local_path):
        return None

    try:
        with open(local_path, "rb") as f:
            data = f.read()
    except Exception:
        return None
    if not data:
        return None

    guessed_type = mimetypes.guess_type(local_path)[0] or ""
    if not _is_valid_cover_payload(payload=data, content_type=guessed_type, source=local_path):
        return None
    ext = _guess_image_extension(source=local_path, content_type=guessed_type)
    return data, ext


def _download_remote_image(candidate_url: str) -> tuple[bytes, str] | None:
    url = str(candidate_url or "").strip()
    if not url:
        return None
    if url.startswith("//"):
        url = f"https:{url}"
    if not (url.startswith("http://") or url.startswith("https://")):
        return None

    headers = dict(_COVER_HTTP_HEADERS)
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
    except Exception:
        pass

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=(_COVER_FETCH_CONNECT_TIMEOUT, _COVER_FETCH_READ_TIMEOUT),
            allow_redirects=True,
        )
        response.raise_for_status()
    except Exception:
        return None

    content = response.content or b""
    if not content:
        return None

    content_type = response.headers.get("Content-Type", "")
    if not _is_valid_cover_payload(payload=content, content_type=content_type, source=url):
        return None
    if not content_type.startswith("image/"):
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext not in _ALLOWED_IMAGE_EXTENSIONS:
            return None

    ext = _guess_image_extension(source=url, content_type=content_type)
    return content, ext


def _read_article_cover_payload(article: Article) -> tuple[bytes, str] | None:
    if not article.cover_image:
        return None
    file_name = str(getattr(article.cover_image, "name", "") or "").strip()
    return _read_field_file_payload(article.cover_image, source_hint=file_name)


def _extract_cover_candidates_from_seo_article(seo_article: SeoArticle) -> list[str]:
    candidates: list[str] = []
    payload = seo_article.rewrite_payload if isinstance(seo_article.rewrite_payload, dict) else {}
    step5_payload = payload.get("step5_quality") if isinstance(payload, dict) else {}
    if isinstance(step5_payload, dict):
        for key in ("cover_image_url", "best_image_url"):
            value = str(step5_payload.get(key) or "").strip()
            if value:
                candidates.append(value)
        selected_images = step5_payload.get("selected_images")
        if isinstance(selected_images, list):
            for item in selected_images:
                if isinstance(item, dict):
                    value = str(item.get("url") or "").strip()
                else:
                    value = str(item or "").strip()
                if value:
                    candidates.append(value)

    media = payload.get("media") if isinstance(payload, dict) else {}
    items = media.get("items") if isinstance(media, dict) else []

    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                value = str(item.get("url") or "").strip()
            else:
                value = str(item or "").strip()
            if value:
                candidates.append(value)

    html_candidates = [payload.get("body_html"), payload.get("final_body_html"), seo_article.body_html]
    for html in html_candidates:
        if not html:
            continue
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', str(html), flags=re.I)
        if match:
            value = str(match.group(1) or "").strip()
            if value:
                candidates.append(value)

    game_name = ""
    if seo_article.game:
        game_name = str(getattr(seo_article.game, "title", "") or "").strip()
    if not game_name:
        game_name = str(seo_article.title or "").strip()

    if game_name:
        candidates.extend(_find_media_asset_urls_for_game(game_name=game_name, limit=8))

    candidates.extend(_find_game_icon_urls(seo_article.game))

    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        key = item.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return deduped


def _collect_existing_cover_signatures(*, exclude_article_id: int | None = None) -> set[str]:
    queryset = Article.objects.exclude(cover_image__isnull=True).exclude(cover_image="")
    if exclude_article_id:
        queryset = queryset.exclude(pk=exclude_article_id)

    signatures: set[str] = set()
    for item in queryset.only("id", "cover_image"):
        payload_result = _read_article_cover_payload(item)
        if payload_result is None:
            continue
        signature = _cover_payload_signature(payload_result[0])
        if signature:
            signatures.add(signature)
    return signatures


def _save_article_cover_payload(*, article: Article, stem: str, payload: bytes, ext: str) -> bool:
    if not _is_valid_cover_payload(payload=payload, content_type="", source=stem):
        return False
    normalized_ext = str(ext or ".jpg").strip().lower()
    if not normalized_ext.startswith("."):
        normalized_ext = f".{normalized_ext}"
    if normalized_ext not in _ALLOWED_IMAGE_EXTENSIONS:
        normalized_ext = ".jpg"
    file_name = f"{stem}-{uuid.uuid4().hex[:10]}{normalized_ext}"
    article.cover_image.save(file_name, ContentFile(payload), save=False)
    return True


def _build_cover_variant_payload(*, base_payload: bytes, seed: str) -> tuple[bytes, str] | None:
    if not base_payload or Image is None:
        return None

    try:
        image = Image.open(BytesIO(base_payload)).convert("RGB")
    except Exception:
        return None

    width, height = image.size
    if width < _MIN_COVER_WIDTH or height < _MIN_COVER_HEIGHT:
        return None

    seed_hex = hashlib.md5(str(seed).encode("utf-8")).hexdigest()
    seed_int = int(seed_hex[:12], 16)
    crop_scale = 0.90 + ((seed_int % 7) * 0.01)
    crop_w = max(_MIN_COVER_WIDTH, min(width, int(width * crop_scale)))
    crop_h = max(_MIN_COVER_HEIGHT, min(height, int(height * crop_scale)))
    max_left = max(0, width - crop_w)
    max_top = max(0, height - crop_h)
    left = (seed_int // 37) % (max_left + 1) if max_left else 0
    top = (seed_int // 97) % (max_top + 1) if max_top else 0

    try:
        working = image.crop((left, top, left + crop_w, top + crop_h))
        resample = getattr(
            getattr(Image, "Resampling", Image),
            "LANCZOS",
            getattr(Image, "LANCZOS", getattr(Image, "BICUBIC", 3)),
        )
        if working.size != (width, height):
            working = working.resize((width, height), resample)
    except Exception:
        return None

    if ImageEnhance is not None:
        contrast = 0.92 + (((seed_int >> 8) % 20) / 100.0)
        saturation = 0.90 + (((seed_int >> 13) % 24) / 100.0)
        brightness = 0.94 + (((seed_int >> 17) % 18) / 100.0)
        working = ImageEnhance.Contrast(working).enhance(contrast)
        working = ImageEnhance.Color(working).enhance(saturation)
        working = ImageEnhance.Brightness(working).enhance(brightness)

    try:
        out = BytesIO()
        working.save(out, format="JPEG", quality=90, optimize=True)
        variant_payload = out.getvalue()
    except Exception:
        return None

    if not _is_valid_cover_payload(
        payload=variant_payload,
        content_type="image/jpeg",
        source="cover-variant.jpg",
    ):
        return None
    return variant_payload, ".jpg"


def _expand_cover_candidates_for_uniqueness(*, game_name: str, existing_candidates: list[str]) -> list[str]:
    normalized_game_name = str(game_name or "").strip()
    if not normalized_game_name:
        return []

    queries = [
        f"{normalized_game_name} official key visual",
        f"{normalized_game_name} gameplay screenshot",
        f"{normalized_game_name} key visual wallpaper",
    ]
    raw_candidates: list[dict[str, str]] = []
    for query in queries[:_COVER_EXTRA_BING_QUERY_COUNT]:
        try:
            raw_candidates.extend(_search_bing_images(query=query, max_pages=2, per_page_target=36))
        except Exception:
            continue

    if not raw_candidates:
        return []

    filtered: list[dict[str, Any]]
    try:
        filtered, _diag = _filter_quality_image_candidates(
            raw_candidates,
            game_name=normalized_game_name,
            limit=24,
            max_checked=160,
        )
    except Exception:
        filtered = raw_candidates

    existing_set = {str(item).strip() for item in existing_candidates if str(item).strip()}
    urls: list[str] = []
    seen: set[str] = set(existing_set)
    for item in filtered:
        if isinstance(item, dict):
            value = str(item.get("url") or "").strip()
        else:
            value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        urls.append(value)
    return urls


def _ensure_article_cover_image(*, article: Article, seo_article: SeoArticle | None = None) -> bool:
    resolved_seo_article = seo_article
    if resolved_seo_article is None:
        resolved_seo_article = (
            SeoArticle.objects.select_related("game")
            .filter(published_article=article)
            .order_by("-updated_at", "-id")
            .first()
        )

    related_game = resolved_seo_article.game if resolved_seo_article and resolved_seo_article.game else article.game
    title_hint = ""
    if resolved_seo_article:
        title_hint = str(resolved_seo_article.title or "").strip()
    if not title_hint:
        title_hint = str(article.title or "").strip()
    if not title_hint and related_game:
        title_hint = str(getattr(related_game, "title", "") or "").strip()

    stem = slugify(title_hint or "seo-article")
    stem = stem[:60] or "seo-article"
    used_signatures = _collect_existing_cover_signatures(exclude_article_id=article.id if article.id else None)

    variant_source: tuple[bytes, str] | None = None
    existing_payload = _read_article_cover_payload(article)
    if existing_payload is not None:
        existing_signature = _cover_payload_signature(existing_payload[0])
        if existing_signature and existing_signature not in used_signatures:
            return False
        variant_source = existing_payload

    if article.cover_image:
        article.cover_image = None

    candidates: list[str] = []
    if resolved_seo_article is not None:
        candidates.extend(_extract_cover_candidates_from_seo_article(resolved_seo_article))
    candidates.extend(_extract_cover_candidates_from_article_content(article))

    game_name = ""
    if related_game:
        game_name = str(getattr(related_game, "title", "") or "").strip()
    if not game_name:
        game_name = title_hint
    if game_name:
        candidates.extend(_find_media_asset_urls_for_game(game_name=game_name, limit=10))
        candidates.extend(_find_game_icon_urls(related_game))

    candidates = _dedupe_cover_candidates(candidates)
    remote_attempts = 0

    for candidate in candidates:
        result = _read_local_media_bytes(candidate)
        if result is None:
            if remote_attempts >= _COVER_MAX_REMOTE_ATTEMPTS:
                continue
            remote_attempts += 1
            result = _download_remote_image(candidate)
        if result is None:
            continue
        image_bytes, ext = result
        signature = _cover_payload_signature(image_bytes)
        if signature and signature in used_signatures:
            if variant_source is None:
                variant_source = (image_bytes, ext)
            continue
        if _save_article_cover_payload(article=article, stem=stem, payload=image_bytes, ext=ext):
            return True

    extra_candidates = _expand_cover_candidates_for_uniqueness(
        game_name=game_name,
        existing_candidates=candidates,
    )
    for candidate in extra_candidates:
        if remote_attempts >= _COVER_MAX_REMOTE_ATTEMPTS:
            break
        remote_attempts += 1
        result = _download_remote_image(candidate)
        if result is None:
            continue
        image_bytes, ext = result
        signature = _cover_payload_signature(image_bytes)
        if signature and signature in used_signatures:
            if variant_source is None:
                variant_source = (image_bytes, ext)
            continue
        if _save_article_cover_payload(article=article, stem=stem, payload=image_bytes, ext=ext):
            return True

    if related_game and getattr(related_game, "icon_image", None):
        icon_payload = _read_field_file_payload(related_game.icon_image, source_hint="game-icon")
        if icon_payload is not None:
            icon_bytes, icon_ext = icon_payload
            icon_signature = _cover_payload_signature(icon_bytes)
            if icon_signature and icon_signature not in used_signatures:
                if _save_article_cover_payload(
                    article=article,
                    stem=stem,
                    payload=icon_bytes,
                    ext=icon_ext,
                ):
                    return True
            if variant_source is None:
                variant_source = icon_payload

    if variant_source is not None:
        source_payload, _source_ext = variant_source
        base_seed = (
            f"{article.id or 0}-"
            f"{getattr(resolved_seo_article, 'id', 0) if resolved_seo_article else 0}-"
            f"{title_hint}"
        )
        for attempt in range(_COVER_UNIQUE_VARIANT_ATTEMPTS):
            variant = _build_cover_variant_payload(
                base_payload=source_payload,
                seed=f"{base_seed}-{attempt}-{uuid.uuid4().hex[:6]}",
            )
            if variant is None:
                continue
            variant_bytes, variant_ext = variant
            variant_signature = _cover_payload_signature(variant_bytes)
            if not variant_signature or variant_signature in used_signatures:
                continue
            if _save_article_cover_payload(
                article=article,
                stem=stem,
                payload=variant_bytes,
                ext=variant_ext,
            ):
                return True

    return False


def _has_usable_cover_image(article: Article) -> bool:
    return _read_article_cover_payload(article) is not None


def _run_bahamut_pipeline(
    *,
    task: CrawlerTask,
    payload: dict,
    request_user,
) -> dict:
    created_by = request_user if request_user and request_user.is_authenticated else None
    game = None
    related_game_id = payload.get("related_game_id")
    if related_game_id:
        game = GamePage.objects.filter(pk=related_game_id).first()

    stop_after_step = _normalize_stop_after_step(payload.get("stop_after_step"))
    run_rewrite = bool(payload.get("run_rewrite", True))
    auto_publish = _to_bool(payload.get("auto_publish"), default=False)
    # Keep generated articles visually consistent: auto-publish must pass Step5 image filtering.
    if auto_publish and stop_after_step < 5:
        stop_after_step = 5
        payload["stop_after_step"] = 5
    rewrite_limit_requested = int(payload.get("rewrite_limit", 3))

    task.status = "crawling"
    task.progress = 5
    task.error_message = ""
    task.started_at = timezone.now()
    task.finished_at = None
    task.request_payload = payload
    task.save(
        update_fields=[
            "status",
            "progress",
            "error_message",
            "started_at",
            "finished_at",
            "request_payload",
            "updated_at",
        ]
    )

    try:
        crawler = BahamutCrawler()

        # Step 1: crawl topic links only.
        requested_keyword = str(payload.get("keyword", task.keyword or "") or "").strip()
        stage1_result = crawler.crawl_board(
            bsn=payload.get("bsn"),
            source_url=payload.get("source_url", task.source_url or ""),
            start_page=payload.get("start_page", 1),
            end_page=payload.get("end_page", 1),
            max_posts=payload.get("max_posts", 20),
            keyword=requested_keyword,
            include_details=False,
        )
        topic_links = stage1_result.get("topic_links", []) or []
        page_errors = stage1_result.get("page_errors", []) or []
        links_count = int(stage1_result.get("links_count", len(topic_links)) or 0)
        stage1_fallback = {
            "attempted_without_keyword": False,
            "activated": False,
            "requested_keyword": requested_keyword,
            "links_before_fallback": links_count,
            "links_after_fallback": links_count,
        }

        # If keyword filtering yields empty list, retry once without keyword.
        if links_count == 0 and requested_keyword:
            stage1_fallback["attempted_without_keyword"] = True
            stage1_retry_result = crawler.crawl_board(
                bsn=payload.get("bsn"),
                source_url=payload.get("source_url", task.source_url or ""),
                start_page=payload.get("start_page", 1),
                end_page=payload.get("end_page", 1),
                max_posts=payload.get("max_posts", 20),
                keyword="",
                include_details=False,
            )
            retry_topic_links = stage1_retry_result.get("topic_links", []) or []
            retry_page_errors = stage1_retry_result.get("page_errors", []) or []
            retry_links_count = int(stage1_retry_result.get("links_count", len(retry_topic_links)) or 0)
            stage1_fallback["links_after_fallback"] = retry_links_count

            if retry_links_count > links_count:
                stage1_fallback["activated"] = True
                stage1_result = stage1_retry_result
                topic_links = retry_topic_links
                page_errors = retry_page_errors
                links_count = retry_links_count

        links_stage_status = _stage_status_from_count(count=links_count, errors=page_errors)

        task.status = "crawling"
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload={
            "pipeline": {
                "stop_after_step": stop_after_step,
                "step_completed": 1,
                "strict_step_mode": True,
            },
            "crawl": {
                "board_url": stage1_result.get("board_url", ""),
                "bsn": stage1_result.get("bsn"),
                "start_page": stage1_result.get("start_page"),
                "end_page": stage1_result.get("end_page"),
                "max_posts": stage1_result.get("max_posts"),
                "keyword": stage1_result.get("keyword", ""),
                "stage1_fallback": stage1_fallback,
                "topic_links": topic_links,
                "links_count": links_count,
                "posts": [],
                "details_count": 0,
                "posts_count": 0,
                "page_errors": page_errors,
                "detail_errors": [],
                "stages": {
                    "stage1_links": {
                        "status": links_stage_status,
                        "count": links_count,
                        "errors_count": len(page_errors),
                    },
                    "stage2_details": {"status": "pending", "count": 0, "errors_count": 0},
                    "stage3_seo_analysis": {"status": "pending", "count": 0, "errors_count": 0},
                    "stage4_seo_generation": {"status": "pending", "count": 0, "errors_count": 0},
                    "stage5_quality_output": {"status": "pending", "count": 0, "errors_count": 0},
                },
            },
            "analysis": {
                "status": "pending",
                "generated_at": "",
                "post_count": 0,
                "items": [],
                "global_keywords": [],
            },
            "rewrite": {
                "enabled": run_rewrite,
                "status": "pending" if run_rewrite else "disabled",
                "rewrite_limit": rewrite_limit_requested,
                "rewrite_target_count": 0,
                "attempted_count": 0,
                "rewrite_count": 0,
                "skipped_count": 0,
                "article_ids": [],
                "errors": [],
                "store_draft": bool(payload.get("store_draft", True) or payload.get("auto_publish", False)),
                "auto_publish": bool(payload.get("auto_publish", False)),
                "media_count": 0,
            },
            "quality": {
                "status": "pending",
                "optimized_count": 0,
                "image_count": 0,
                "errors": [],
                "items": [],
            },
        },
        )
        task.progress = 25
        task.result_count = 0
        task.save(update_fields=["status", "progress", "result_count", "result_payload", "updated_at"])

        if stop_after_step == 1:
            task.status = "completed"
            task.finished_at = timezone.now()
            task.result_payload = _attach_operator_summary(
                task_id=task.id,
                task_status=task.status,
                result_payload=task.result_payload or {},
            )
            task.save(update_fields=["status", "finished_at", "result_payload", "updated_at"])
            return {
                "task_id": task.id,
                "status": task.status,
                "step_completed": 1,
                "next_step": 2,
                "links_count": links_count,
                "details_count": 0,
                "rewrite_count": 0,
                "article_ids": [],
                "errors": [],
                "media_count": 0,
                "result_payload": task.result_payload,
                "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
            }

        # Step 2: extract details from links.
        stage2_result = crawler.crawl_topic_details(topic_links=topic_links)
        posts = stage2_result.get("posts", []) or []
        detail_errors = stage2_result.get("detail_errors", []) or []
        details_count = int(stage2_result.get("details_count", len(posts)) or 0)
        details_stage_status = _stage_status_from_count(count=details_count, errors=detail_errors)

        result_payload = task.result_payload or {}
        crawl_payload = result_payload.setdefault("crawl", {})
        crawl_payload["posts"] = posts
        crawl_payload["details_count"] = details_count
        crawl_payload["posts_count"] = details_count
        crawl_payload["detail_errors"] = detail_errors
        crawl_payload["stages"]["stage2_details"] = {
            "status": details_stage_status,
            "count": details_count,
            "errors_count": len(detail_errors),
        }
        result_payload["pipeline"]["step_completed"] = 2

        task.status = "enriching"
        task.progress = 50
        task.result_count = details_count
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload=result_payload,
        )
        task.save(update_fields=["status", "progress", "result_count", "result_payload", "updated_at"])

        if stop_after_step == 2:
            task.status = "completed"
            task.finished_at = timezone.now()
            task.result_payload = _attach_operator_summary(
                task_id=task.id,
                task_status=task.status,
                result_payload=task.result_payload or {},
            )
            task.save(update_fields=["status", "finished_at", "result_payload", "updated_at"])
            return {
                "task_id": task.id,
                "status": task.status,
                "step_completed": 2,
                "next_step": 3,
                "links_count": links_count,
                "details_count": details_count,
                "rewrite_count": 0,
                "article_ids": [],
                "errors": detail_errors,
                "media_count": 0,
                "result_payload": task.result_payload,
                "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
            }

        # Step 3: SEO analysis.
        analysis_payload = _build_seo_analysis(
            posts=posts,
            payload=payload,
            task=task,
            game=game,
        )
        result_payload["analysis"] = analysis_payload
        result_payload["pipeline"]["step_completed"] = 3
        result_payload["crawl"]["stages"]["stage3_seo_analysis"] = {
            "status": analysis_payload.get("status", "empty"),
            "count": len(analysis_payload.get("items") or []),
            "errors_count": 0,
        }

        task.status = "seoing"
        task.progress = 75
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload=result_payload,
        )
        task.save(update_fields=["status", "progress", "result_payload", "updated_at"])

        if stop_after_step == 3:
            task.status = "completed"
            task.finished_at = timezone.now()
            task.result_payload = _attach_operator_summary(
                task_id=task.id,
                task_status=task.status,
                result_payload=task.result_payload or {},
            )
            task.save(update_fields=["status", "finished_at", "result_payload", "updated_at"])
            return {
                "task_id": task.id,
                "status": task.status,
                "step_completed": 3,
                "next_step": 4,
                "links_count": links_count,
                "details_count": details_count,
                "rewrite_count": 0,
                "article_ids": [],
                "errors": [],
                "media_count": 0,
                "result_payload": task.result_payload,
                "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
            }

        # Step 4: AI generation with media combination.
        article_ids: list[int] = []
        rewrite_errors: list[str] = []
        rewrite_count = 0
        rewrite_attempted = 0
        rewrite_skipped = 0
        media_count = 0
        custom_keywords = payload.get("custom_keywords") or []
        rewrite_limit = min(max(rewrite_limit_requested, 1), len(posts)) if posts else 0
        analysis_items = (analysis_payload.get("items") or []) if isinstance(analysis_payload, dict) else []

        if run_rewrite and not posts:
            rewrite_errors.append("stage2: no detail content extracted, generation skipped")

        if run_rewrite and rewrite_limit > 0:
            for idx, post in enumerate(posts[:rewrite_limit], start=1):
                post_text = "\n".join(
                    part.strip()
                    for part in [
                        str(post.get("content") or ""),
                        str(post.get("title") or ""),
                        str(post.get("snippet") or ""),
                    ]
                    if str(part or "").strip()
                ).strip()
                if not post_text:
                    rewrite_skipped += 1
                    rewrite_errors.append(f"post_{idx}: empty content")
                    continue

                analysis_item = _get_analysis_item_for_post(
                    analysis_items=analysis_items,
                    post=post,
                    index=idx - 1,
                )
                step_keywords = merge_unique_tags(
                    base_tags=analysis_item.get("rewrite_keywords") or analysis_item.get("focus_keywords") or [],
                    extra_tags=custom_keywords,
                    limit=12,
                )

                rewrite_attempted += 1
                try:
                    base_game_name = game.title if game else (task.keyword or payload.get("keyword") or "Bahamut Game")
                    link_game = game or _resolve_related_game_by_name(base_game_name)
                    if game is None and link_game is not None:
                        game = link_game
                    game_name = link_game.title if link_game else base_game_name
                    source_title_resolved, source_url_resolved = _build_preferred_source_reference(
                        game=link_game,
                        game_name=game_name,
                        fallback_title=post.get("title", ""),
                        fallback_url=post.get("topic_url", ""),
                    )
                    rewrite_result = rewrite_bahamut_text(
                        raw_text=post_text,
                        game_name=game_name,
                        keywords=step_keywords,
                    )
                    rewrite_count += 1

                    media_items = build_media_items(
                        image_urls=post.get("image_urls") or [],
                        game_name=game_name,
                    )
                    media_fallback_used = False
                    media_fallback_source = ""
                    if not media_items:
                        fallback_urls = _find_media_asset_urls_for_game(game_name=game_name, limit=6)
                        if fallback_urls:
                            media_fallback_source = "media_asset_library"
                        if not fallback_urls:
                            fallback_urls = _find_game_icon_urls(link_game)
                            if fallback_urls:
                                media_fallback_source = "game_icon"
                        if fallback_urls:
                            media_items = build_media_items(
                                image_urls=fallback_urls,
                                game_name=game_name,
                            )
                            media_fallback_used = True
                    media_count += len(media_items)
                    gallery_html = build_media_gallery_html(media_items)

                    merged_tags = merge_unique_tags(
                        base_tags=rewrite_result.get("tags") or [],
                        extra_tags=step_keywords,
                    )

                    body_html = compose_rich_seo_article_html(
                        title=rewrite_result.get("title", ""),
                        body_html=rewrite_result.get("body_html", ""),
                        game_name=game_name,
                        summary=analysis_item.get("summary") or rewrite_result.get("meta_description", ""),
                        keywords=merged_tags,
                        search_intent=analysis_item.get("search_intent", ""),
                        source_title=source_title_resolved or post.get("title", ""),
                        source_url=source_url_resolved,
                        media_gallery_html=gallery_html,
                        media_items=media_items,
                        generated_at=timezone.now(),
                    )
                    body_html = inject_game_internal_link(
                        body_html=body_html,
                        game_id=link_game.id if link_game else None,
                        game_title=link_game.title if link_game else game_name,
                        google_play_id=link_game.google_play_id if link_game else "",
                    )

                    meta = build_meta_fields(
                        title=rewrite_result.get("title", ""),
                        body_html=body_html,
                        default_title=game_name,
                    )
                    standalone_html = build_standalone_seo_html_document(
                        title=rewrite_result.get("title", ""),
                        meta_description=meta["meta_description"],
                        meta_keywords=",".join(merged_tags[:10]),
                        body_html=body_html,
                    )

                    rewrite_payload = dict(rewrite_result)
                    rewrite_payload["analysis"] = analysis_item
                    rewrite_payload["media"] = {
                        "count": len(media_items),
                        "fallback_used": media_fallback_used,
                        "fallback_source": media_fallback_source,
                        "fallback_from_asset_library": media_fallback_source == "media_asset_library",
                        "items": media_items,
                    }
                    rewrite_payload["final_body_html"] = body_html
                    rewrite_payload["standalone_html"] = standalone_html
                    rewrite_payload["layout"] = {
                        "style": "rich_seo_v1",
                        "summary_block": True,
                        "quick_facts_table": True,
                        "metadata_footer": True,
                    }
                    rewrite_payload["source_original"] = {
                        "title": post.get("title", ""),
                        "url": post.get("topic_url", ""),
                    }
                    rewrite_payload["source_resolved"] = {
                        "title": source_title_resolved or post.get("title", ""),
                        "url": source_url_resolved,
                    }
                    if link_game:
                        rewrite_payload["internal_link"] = f"/games/{link_game.id}"

                    should_store = bool(payload.get("store_draft", True) or payload.get("auto_publish", False))
                    if should_store:
                        article = SeoArticle.objects.create(
                            title=rewrite_result["title"],
                            game=link_game,
                            task=task,
                            source_platform="bahamut",
                            source_title=source_title_resolved or post.get("title", ""),
                            source_url=source_url_resolved,
                            raw_text=post_text,
                            body_html=body_html,
                            tags=merged_tags,
                            meta_title=meta["meta_title"],
                            meta_description=meta["meta_description"],
                            rewrite_model=rewrite_result.get("diagnostics", {}).get("model", ""),
                            rewrite_payload=rewrite_payload,
                            created_by=created_by,
                            status="draft",
                        )
                        if payload.get("auto_publish", False):
                            _publish_seo_article(
                                seo_article=article,
                                request_user=request_user,
                                publish_now=bool(payload.get("publish_now", True)),
                                publish_at=payload.get("publish_at"),
                            )
                        article_ids.append(article.id)
                except Exception as exc:
                    rewrite_errors.append(f"post_{idx}: {str(exc)[:180]}")

                if rewrite_limit > 0:
                    task.progress = min(95, 75 + int((idx / rewrite_limit) * 20))
                    task.save(update_fields=["progress", "updated_at"])

        rewrite_status = "disabled"
        if run_rewrite:
            if rewrite_count > 0:
                rewrite_status = "completed"
            elif rewrite_limit == 0:
                rewrite_status = "skipped_no_content"
            elif rewrite_errors:
                rewrite_status = "failed"
            else:
                rewrite_status = "skipped"

        result_payload["pipeline"]["step_completed"] = 4
        result_payload["rewrite"] = {
            "enabled": run_rewrite,
            "status": rewrite_status,
            "rewrite_limit": rewrite_limit_requested,
            "rewrite_target_count": rewrite_limit,
            "attempted_count": rewrite_attempted,
            "rewrite_count": rewrite_count,
            "skipped_count": rewrite_skipped,
            "article_ids": article_ids,
            "errors": rewrite_errors,
            "store_draft": bool(payload.get("store_draft", True) or payload.get("auto_publish", False)),
            "auto_publish": bool(payload.get("auto_publish", False)),
            "media_count": media_count,
        }
        result_payload["crawl"]["stages"]["stage4_seo_generation"] = {
            "status": rewrite_status if run_rewrite else "disabled",
            "count": rewrite_count,
            "errors_count": len(rewrite_errors),
        }
        result_payload["quality"] = {
            "status": "pending",
            "optimized_count": 0,
            "image_count": 0,
            "errors": [],
            "items": [],
        }

        if stop_after_step == 4:
            result_payload["crawl"]["stages"]["stage5_quality_output"] = {
                "status": "pending",
                "count": 0,
                "errors_count": 0,
            }
            result_payload["summary"] = {
                "links_count": links_count,
                "details_count": details_count,
                "posts_count": details_count,
                "analysis_count": len(analysis_items),
                "rewrite_target_count": rewrite_limit,
                "rewrite_count": rewrite_count,
                "article_ids": article_ids,
                "crawl_errors_count": len(page_errors) + len(detail_errors),
                "rewrite_errors_count": len(rewrite_errors),
                "media_count": media_count,
                "quality_count": 0,
                "quality_image_count": 0,
                "quality_errors_count": 0,
                "cover_expected": True,
            }
            task.status = "seoing"
            task.progress = 92
            task.result_payload = _attach_operator_summary(
                task_id=task.id,
                task_status=task.status,
                result_payload=result_payload,
            )
            task.save(update_fields=["status", "progress", "result_payload", "updated_at"])
            task.status = "completed"
            task.finished_at = timezone.now()
            task.result_payload = _attach_operator_summary(
                task_id=task.id,
                task_status=task.status,
                result_payload=task.result_payload or {},
            )
            task.save(update_fields=["status", "finished_at", "result_payload", "updated_at"])
            return {
                "task_id": task.id,
                "status": task.status,
                "step_completed": 4,
                "next_step": 5,
                "links_count": links_count,
                "details_count": details_count,
                "rewrite_count": rewrite_count,
                "article_ids": article_ids,
                "errors": rewrite_errors,
                "media_count": media_count,
                "result_payload": task.result_payload,
                "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
            }

        # Step 5: quality polish + Bing paragraph images.
        quality_items: list[dict[str, Any]] = []
        quality_errors: list[str] = []
        quality_count = 0
        quality_image_count = 0

        task.status = "publishing"
        task.progress = 94
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload=result_payload,
        )
        task.save(update_fields=["status", "progress", "result_payload", "updated_at"])

        if run_rewrite and article_ids:
            for idx, article_id in enumerate(article_ids, start=1):
                try:
                    seo_article = (
                        SeoArticle.objects.select_related("game", "published_article")
                        .filter(pk=article_id)
                        .first()
                    )
                    if not seo_article:
                        quality_errors.append(f"step5_article_{article_id}: draft not found")
                        continue

                    rewrite_payload = (
                        dict(seo_article.rewrite_payload)
                        if isinstance(seo_article.rewrite_payload, dict)
                        else {}
                    )
                    media_payload = rewrite_payload.get("media") if isinstance(rewrite_payload, dict) else {}
                    media_items_payload = media_payload.get("items") if isinstance(media_payload, dict) else []
                    seed_urls: list[str] = []
                    if isinstance(media_items_payload, list):
                        for item in media_items_payload:
                            if isinstance(item, dict):
                                value = str(item.get("url") or "").strip()
                            else:
                                value = str(item or "").strip()
                            if value:
                                seed_urls.append(value)

                    step5_game_name = seo_article.game.title if seo_article.game else (task.keyword or "游戏")
                    link_game = seo_article.game or _resolve_related_game_by_name(step5_game_name)
                    if not seed_urls:
                        seed_urls = _find_media_asset_urls_for_game(
                            game_name=link_game.title if link_game else step5_game_name,
                            limit=6,
                        )
                    if not seed_urls:
                        seed_urls = _find_game_icon_urls(link_game)
                    resolved_source_title, resolved_source_url = _build_preferred_source_reference(
                        game=link_game,
                        game_name=step5_game_name,
                        fallback_title=seo_article.source_title or seo_article.title,
                        fallback_url=seo_article.source_url or "",
                    )

                    quality_result = run_step5_quality_enhancement(
                        title=seo_article.title,
                        body_html=seo_article.body_html,
                        game_name=step5_game_name,
                        keywords=seo_article.tags or [],
                        source_title=resolved_source_title or seo_article.title,
                        source_url=resolved_source_url,
                        image_seed_urls=seed_urls,
                        generated_at=timezone.now(),
                    )
                    final_body_html = str(quality_result.get("body_html") or seo_article.body_html or "").strip()
                    final_body_html = inject_game_internal_link(
                        body_html=final_body_html,
                        game_id=link_game.id if link_game else None,
                        game_title=link_game.title if link_game else step5_game_name,
                        google_play_id=link_game.google_play_id if link_game else "",
                    )
                    final_meta_title = str(quality_result.get("meta_title") or seo_article.meta_title or seo_article.title)
                    final_meta_description = str(
                        quality_result.get("meta_description")
                        or seo_article.meta_description
                        or ""
                    )
                    selected_images = quality_result.get("selected_images") or []
                    selected_image_count = len(selected_images) if isinstance(selected_images, list) else 0

                    standalone_html = build_standalone_seo_html_document(
                        title=seo_article.title,
                        meta_description=final_meta_description,
                        meta_keywords=",".join((seo_article.tags or [])[:10]),
                        body_html=final_body_html,
                    )

                    rewrite_payload["step5_quality"] = quality_result.get("diagnostics") or {}
                    rewrite_payload["step5_quality"]["selected_images"] = selected_images
                    rewrite_payload["step5_quality"]["cover_image_url"] = str(quality_result.get("cover_image_url") or "")
                    rewrite_payload["final_body_html"] = final_body_html
                    rewrite_payload["standalone_html"] = standalone_html
                    rewrite_payload["layout"] = {
                        **(rewrite_payload.get("layout") or {}),
                        "style": "rich_seo_v2_step5",
                        "step5_quality_enabled": True,
                    }
                    if selected_image_count > 0:
                        rewrite_payload["media"] = {
                            "count": selected_image_count,
                            "fallback_used": False,
                            "fallback_source": "bing_step5",
                            "fallback_from_asset_library": False,
                            "items": selected_images,
                        }

                    seo_article.body_html = final_body_html
                    seo_article.meta_title = final_meta_title[:60]
                    seo_article.meta_description = final_meta_description[:160]
                    seo_article.source_title = resolved_source_title or seo_article.source_title
                    seo_article.source_url = resolved_source_url or seo_article.source_url
                    if seo_article.game_id is None and link_game is not None:
                        seo_article.game = link_game
                    seo_article.rewrite_payload = rewrite_payload
                    seo_article.save(
                        update_fields=[
                            "body_html",
                            "meta_title",
                            "meta_description",
                            "source_title",
                            "source_url",
                            "game",
                            "rewrite_payload",
                            "updated_at",
                        ]
                    )

                    if seo_article.published_article_id:
                        _publish_seo_article(
                            seo_article=seo_article,
                            request_user=request_user,
                            publish_now=seo_article.status == "published",
                            publish_at=seo_article.publish_at.isoformat() if seo_article.publish_at else None,
                        )

                    quality_count += 1
                    quality_image_count += selected_image_count
                    quality_items.append(
                        {
                            "seo_article_id": seo_article.id,
                            "status": "completed",
                            "selected_image_count": selected_image_count,
                        }
                    )
                except Exception as exc:
                    quality_errors.append(f"step5_article_{article_id}: {str(exc)[:180]}")

                if article_ids:
                    task.progress = min(99, 94 + int((idx / len(article_ids)) * 5))
                    task.save(update_fields=["progress", "updated_at"])
        elif not run_rewrite:
            quality_errors.append("step5 skipped: run_rewrite=false")
        else:
            quality_errors.append("step5 skipped: no stored seo drafts for optimization")

        quality_status = "disabled"
        if run_rewrite:
            if quality_count > 0 and quality_errors:
                quality_status = "partial"
            elif quality_count > 0:
                quality_status = "completed"
            elif article_ids and quality_errors:
                quality_status = "failed"
            elif not article_ids:
                quality_status = "skipped_no_draft"
            else:
                quality_status = "skipped"

        result_payload["pipeline"]["step_completed"] = 5
        result_payload["quality"] = {
            "status": quality_status,
            "optimized_count": quality_count,
            "image_count": quality_image_count,
            "errors": quality_errors,
            "items": quality_items,
        }
        result_payload["crawl"]["stages"]["stage5_quality_output"] = {
            "status": quality_status if run_rewrite else "disabled",
            "count": quality_count,
            "errors_count": len(quality_errors),
        }
        result_payload["summary"] = {
            "links_count": links_count,
            "details_count": details_count,
            "posts_count": details_count,
            "analysis_count": len(analysis_items),
            "rewrite_target_count": rewrite_limit,
            "rewrite_count": rewrite_count,
            "article_ids": article_ids,
            "crawl_errors_count": len(page_errors) + len(detail_errors),
            "rewrite_errors_count": len(rewrite_errors),
            "media_count": media_count,
            "quality_count": quality_count,
            "quality_image_count": quality_image_count,
            "quality_errors_count": len(quality_errors),
            "cover_expected": True,
        }

        task.status = "completed"
        task.progress = 100
        task.finished_at = timezone.now()
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload=result_payload,
        )
        task.save(update_fields=["status", "progress", "finished_at", "result_payload", "updated_at"])

        return {
            "task_id": task.id,
            "status": task.status,
            "step_completed": 5,
            "next_step": None,
            "links_count": links_count,
            "details_count": details_count,
            "rewrite_count": rewrite_count,
            "article_ids": article_ids,
            "errors": [*rewrite_errors, *quality_errors],
            "media_count": media_count,
            "result_payload": task.result_payload,
            "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
        }
    except Exception as exc:
        task.status = "failed"
        task.finished_at = timezone.now()
        task.error_message = str(exc)[:1000]
        task.result_payload = _attach_operator_summary(
            task_id=task.id,
            task_status=task.status,
            result_payload={
                "summary": {"failed": True},
                "error": task.error_message,
            },
        )
        task.save(
            update_fields=[
                "status",
                "finished_at",
                "error_message",
                "result_payload",
                "updated_at",
            ]
        )
        return {
            "task_id": task.id,
            "status": task.status,
            "error": task.error_message,
            "result_payload": task.result_payload,
            "operator_summary": (task.result_payload or {}).get("operator_summary", {}),
        }


def _publish_seo_article(
    *,
    seo_article: SeoArticle,
    request_user,
    publish_now: bool = True,
    publish_at: str | None = None,
) -> Article:
    created_by = request_user if request_user and request_user.is_authenticated else None
    article = seo_article.published_article
    if article is None:
        article = Article()

    category = ArticleCategory.objects.filter(is_active=True).order_by("sort_order", "id").first()
    if category:
        article.category = category

    article.title = seo_article.title
    related_game = seo_article.game or _resolve_related_game_by_name(seo_article.title)
    article.game = related_game
    article.author = created_by if created_by else article.author
    summary_seed = sanitize_seo_summary_text(
        seo_article.meta_description or "",
        game_name=related_game.title if related_game else seo_article.title,
        limit=500,
    )
    if not summary_seed:
        summary_seed = str(seo_article.meta_description or "").strip()
    article.excerpt = summary_seed[:500]
    article.summary = summary_seed[:500]
    article.content = seo_article.body_html
    article.title_i18n = _sync_primary_locale_i18n(article.title_i18n, locale="zh-CN", text=article.title)
    article.excerpt_i18n = _sync_primary_locale_i18n(
        article.excerpt_i18n, locale="zh-CN", text=article.excerpt
    )
    article.summary_i18n = _sync_primary_locale_i18n(
        article.summary_i18n, locale="zh-CN", text=article.summary
    )
    article.content_i18n = _sync_primary_locale_i18n(
        article.content_i18n, locale="zh-CN", text=article.content
    )
    article.meta_title = (seo_article.meta_title or seo_article.title)[:200]
    article.meta_description = (seo_article.meta_description or "")[:300]
    article.meta_keywords = ",".join((seo_article.tags or [])[:10])[:200]
    article.status = "published" if publish_now else "draft"
    if publish_now:
        article.published_at = timezone.now()
    article.save()

    if _ensure_article_cover_image(article=article, seo_article=seo_article):
        article.save(update_fields=["cover_image", "updated_at"])

    tag_objects = []
    for raw_tag in (seo_article.tags or [])[:12]:
        tag_name = str(raw_tag).strip()
        if not tag_name:
            continue
        tag_obj, _ = ArticleTag.objects.get_or_create(name=tag_name[:50])
        tag_objects.append(tag_obj)
    article.tags.set(tag_objects)

    publish_dt = parse_datetime(publish_at) if isinstance(publish_at, str) else None
    seo_article.published_article = article
    if seo_article.game_id is None and related_game is not None:
        seo_article.game = related_game
    seo_article.status = "published" if publish_now else "review"
    if publish_now:
        seo_article.published_at = timezone.now()
    if publish_dt:
        seo_article.publish_at = publish_dt
    seo_article.save(
        update_fields=[
            "published_article",
            "game",
            "status",
            "published_at",
            "publish_at",
            "updated_at",
        ]
    )
    return article


def _sync_primary_locale_i18n(existing_map: Any, *, locale: str, text: str) -> dict[str, str]:
    data = dict(existing_map) if isinstance(existing_map, dict) else {}
    value = str(text or "").strip()
    if not value:
        return data

    normalized_locale = str(locale or "").strip() or "zh-CN"
    aliases = [
        normalized_locale,
        normalized_locale.lower(),
        normalized_locale.replace("-", "_"),
        normalized_locale.lower().replace("-", "_"),
    ]
    for alias in aliases:
        if alias:
            data[alias] = value
    return data


def _find_media_asset_urls_for_game(game_name: str, limit: int = 4) -> list[str]:
    keyword = (game_name or "").strip()
    if not keyword:
        return []

    try:
        rows = (
            MediaAsset.objects.filter(
                Q(name__icontains=keyword) | Q(alt_text__icontains=keyword)
            )
            .order_by("-updated_at")[:limit]
        )
    except Exception:
        return []

    urls: list[str] = []
    seen: set[str] = set()
    for asset in rows:
        value = ""
        try:
            value = asset.file.url if asset.file else ""
        except Exception:
            value = ""
        if not value or value in seen:
            continue
        seen.add(value)
        urls.append(value)
    return urls


def _find_game_icon_urls(game: GamePage | None) -> list[str]:
    if not game:
        return []

    urls: list[str] = []
    seen: set[str] = set()

    external_url = str(getattr(game, "icon_external_url", "") or "").strip()
    if external_url and external_url not in seen:
        seen.add(external_url)
        urls.append(external_url)

    try:
        local_url = str(game.icon_image.url if getattr(game, "icon_image", None) else "").strip()
    except Exception:
        local_url = ""
    if local_url and local_url not in seen:
        seen.add(local_url)
        urls.append(local_url)

    return urls


def _extract_seed_urls_from_rewrite_payload(payload: dict[str, Any]) -> list[str]:
    media = payload.get("media") if isinstance(payload, dict) else {}
    items = media.get("items") if isinstance(media, dict) else []
    urls: list[str] = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                value = str(item.get("url") or "").strip()
            else:
                value = str(item or "").strip()
            if value:
                urls.append(value)
    return urls


def _refresh_seo_article_source_and_media(
    *,
    seo_article: SeoArticle,
    task_keyword: str = "",
    request_user=None,
) -> dict[str, Any]:
    rewrite_payload = (
        dict(seo_article.rewrite_payload)
        if isinstance(seo_article.rewrite_payload, dict)
        else {}
    )
    game_name = (
        seo_article.game.title
        if seo_article.game
        else (task_keyword or (seo_article.task.keyword if seo_article.task else "") or seo_article.title or "游戏")
    )
    link_game = seo_article.game or _resolve_related_game_by_name(game_name)
    resolved_source_title, resolved_source_url = _build_preferred_source_reference(
        game=link_game,
        game_name=game_name,
        fallback_title=seo_article.source_title or seo_article.title,
        fallback_url=seo_article.source_url or "",
    )

    seed_urls = _extract_seed_urls_from_rewrite_payload(rewrite_payload)
    if not seed_urls:
        seed_urls = _find_media_asset_urls_for_game(game_name=game_name, limit=8)
    if not seed_urls:
        seed_urls = _find_game_icon_urls(link_game)

    quality_result = run_step5_quality_enhancement(
        title=seo_article.title,
        body_html=seo_article.body_html,
        game_name=game_name,
        keywords=seo_article.tags or [],
        source_title=resolved_source_title or seo_article.title,
        source_url=resolved_source_url,
        image_seed_urls=seed_urls,
        generated_at=timezone.now(),
    )

    final_body_html = str(quality_result.get("body_html") or seo_article.body_html or "").strip()
    final_body_html = inject_game_internal_link(
        body_html=final_body_html,
        game_id=link_game.id if link_game else None,
        game_title=link_game.title if link_game else game_name,
        google_play_id=link_game.google_play_id if link_game else "",
    )
    final_meta_title = str(quality_result.get("meta_title") or seo_article.meta_title or seo_article.title)
    final_meta_description = str(
        quality_result.get("meta_description")
        or seo_article.meta_description
        or ""
    )
    selected_images = quality_result.get("selected_images") or []
    selected_image_count = len(selected_images) if isinstance(selected_images, list) else 0

    standalone_html = build_standalone_seo_html_document(
        title=seo_article.title,
        meta_description=final_meta_description,
        meta_keywords=",".join((seo_article.tags or [])[:10]),
        body_html=final_body_html,
    )

    rewrite_payload["step5_quality"] = quality_result.get("diagnostics") or {}
    rewrite_payload["step5_quality"]["selected_images"] = selected_images
    rewrite_payload["step5_quality"]["cover_image_url"] = str(quality_result.get("cover_image_url") or "")
    rewrite_payload["final_body_html"] = final_body_html
    rewrite_payload["standalone_html"] = standalone_html
    rewrite_payload["layout"] = {
        **(rewrite_payload.get("layout") or {}),
        "style": "rich_seo_v2_step5",
        "step5_quality_enabled": True,
    }
    rewrite_payload["source_resolved"] = {
        "title": resolved_source_title or seo_article.source_title,
        "url": resolved_source_url or seo_article.source_url,
    }
    if selected_image_count > 0:
        rewrite_payload["media"] = {
            "count": selected_image_count,
            "fallback_used": False,
            "fallback_source": "refresh_step5",
            "fallback_from_asset_library": False,
            "items": selected_images,
        }
    else:
        rewrite_payload["media"] = {
            "count": 0,
            "fallback_used": False,
            "fallback_source": "refresh_step5_no_image",
            "fallback_from_asset_library": False,
            "items": [],
        }

    seo_article.body_html = final_body_html
    seo_article.meta_title = final_meta_title[:60]
    seo_article.meta_description = final_meta_description[:160]
    seo_article.source_title = resolved_source_title or seo_article.source_title
    seo_article.source_url = resolved_source_url or seo_article.source_url
    if seo_article.game_id is None and link_game is not None:
        seo_article.game = link_game
    seo_article.rewrite_payload = rewrite_payload
    seo_article.save(
        update_fields=[
            "body_html",
            "meta_title",
            "meta_description",
            "source_title",
            "source_url",
            "game",
            "rewrite_payload",
            "updated_at",
        ]
    )

    if seo_article.published_article_id:
        _publish_seo_article(
            seo_article=seo_article,
            request_user=request_user,
            publish_now=seo_article.status == "published",
            publish_at=seo_article.publish_at.isoformat() if seo_article.publish_at else None,
        )

    return {
        "seo_article_id": seo_article.id,
        "status": "completed",
        "selected_image_count": selected_image_count,
        "source_url": seo_article.source_url,
    }


def _sync_seo_article_rewrite_payload(seo_article: SeoArticle) -> None:
    payload = dict(seo_article.rewrite_payload) if isinstance(seo_article.rewrite_payload, dict) else {}
    changed = False

    if payload.get("title") != seo_article.title:
        payload["title"] = seo_article.title
        changed = True
    if payload.get("body_html") != seo_article.body_html:
        payload["body_html"] = seo_article.body_html
        changed = True
    if payload.get("final_body_html") != seo_article.body_html:
        payload["final_body_html"] = seo_article.body_html
        changed = True
    if payload.get("meta_title") != seo_article.meta_title:
        payload["meta_title"] = seo_article.meta_title
        changed = True
    if payload.get("meta_description") != seo_article.meta_description:
        payload["meta_description"] = seo_article.meta_description
        changed = True
    if payload.get("tags") != (seo_article.tags or []):
        payload["tags"] = seo_article.tags or []
        changed = True

    if changed:
        payload["layout"] = {
            **(payload.get("layout") or {}),
            "manual_edited": True,
        }
        payload["standalone_html"] = build_standalone_seo_html_document(
            title=seo_article.title,
            meta_description=seo_article.meta_description,
            meta_keywords=",".join((seo_article.tags or [])[:10]),
            body_html=seo_article.body_html,
        )
        seo_article.rewrite_payload = payload
        seo_article.save(update_fields=["rewrite_payload", "updated_at"])


class CrawlerTaskViewSet(viewsets.ModelViewSet):
    queryset = CrawlerTask.objects.all()
    serializer_class = CrawlerTaskSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "source_platform", "keyword"]
    search_fields = ["name", "keyword", "source_url"]
    ordering_fields = ["created_at", "updated_at", "progress"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["post"], url_path="run")
    def run_new_task(self, request):
        input_serializer = BahamutTaskRunSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        payload = dict(input_serializer.validated_data)

        source_url = payload.get("source_url", "")
        bsn = payload.get("bsn")
        if not source_url and bsn:
            source_url = f"https://forum.gamer.com.tw/B.php?bsn={bsn}"
            payload["source_url"] = source_url
        keyword = (payload.get("keyword") or str(bsn or "") or source_url or "bahamut").strip()
        created_by = request.user if request.user and request.user.is_authenticated else None

        task = CrawlerTask.objects.create(
            name=f"Bahamut Crawl {keyword}"[:200],
            source_platform="bahamut",
            source_url=source_url,
            keyword=keyword[:120],
            status="pending",
            progress=0,
            triggered_by=created_by,
            request_payload=payload,
        )

        result = _run_bahamut_pipeline(task=task, payload=payload, request_user=request.user)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="run")
    def run_existing_task(self, request, pk=None):
        task = self.get_object()
        payload = dict(task.request_payload or {})
        payload.update(request.data or {})
        if not payload.get("source_url"):
            payload["source_url"] = task.source_url
        if not payload.get("keyword"):
            payload["keyword"] = task.keyword

        input_serializer = BahamutTaskRunSerializer(data=payload)
        input_serializer.is_valid(raise_exception=True)
        payload = dict(input_serializer.validated_data)

        result = _run_bahamut_pipeline(task=task, payload=payload, request_user=request.user)
        return Response(result, status=status.HTTP_200_OK)


class SeoKeywordWeightViewSet(viewsets.ModelViewSet):
    queryset = SeoKeywordWeight.objects.all()
    serializer_class = SeoKeywordWeightSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "keyword_group", "intent", "language", "locale"]
    search_fields = ["keyword", "notes"]
    ordering_fields = ["weight", "created_at", "updated_at"]
    ordering = ["-weight", "keyword"]


class SeoArticleViewSet(viewsets.ModelViewSet):
    queryset = SeoArticle.objects.select_related("game", "task", "published_article")
    serializer_class = SeoArticleSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "source_platform", "game", "task"]
    search_fields = ["title", "source_title", "meta_description"]
    ordering_fields = ["created_at", "updated_at", "publish_at", "published_at", "seo_score"]
    ordering = ["-created_at"]

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        try:
            seo_article = self.get_object()
            _sync_seo_article_rewrite_payload(seo_article)
        except Exception:
            pass
        return response

    @action(detail=False, methods=["post"], url_path="refresh-legacy-drafts")
    def refresh_legacy_drafts(self, request):
        try:
            limit = int(request.data.get("limit", 30))
        except Exception:
            limit = 30
        limit = max(1, min(200, limit))

        include_published = _to_bool(request.data.get("include_published"), default=False)
        statuses = ["draft", "review"]
        if include_published:
            statuses.append("published")

        queryset = (
            self.get_queryset()
            .select_related("game", "task", "published_article")
            .filter(status__in=statuses)
            .order_by("-updated_at", "-id")[:limit]
        )

        items: list[dict[str, Any]] = []
        errors: list[str] = []
        updated_ids: list[int] = []

        for article in queryset:
            try:
                item = _refresh_seo_article_source_and_media(
                    seo_article=article,
                    task_keyword=article.task.keyword if article.task else "",
                    request_user=request.user,
                )
                items.append(item)
                updated_ids.append(article.id)
            except Exception as exc:
                errors.append(f"article_{article.id}: {str(exc)[:180]}")

        return Response(
            {
                "status": "completed" if not errors else ("partial" if updated_ids else "failed"),
                "target_count": len(queryset),
                "updated_count": len(updated_ids),
                "error_count": len(errors),
                "updated_ids": updated_ids,
                "items": items,
                "errors": errors,
                "include_published": include_published,
                "limit": limit,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        seo_article = self.get_object()
        publish_now = _to_bool(request.data.get("publish_now"), default=True)
        run_step5 = _to_bool(request.data.get("run_step5"), default=True)
        quality_result = None

        if run_step5:
            try:
                quality_result = _refresh_seo_article_source_and_media(
                    seo_article=seo_article,
                    task_keyword=seo_article.task.keyword if seo_article.task else "",
                    request_user=request.user,
                )
                seo_article.refresh_from_db()
            except Exception as exc:
                return Response(
                    {
                        "seo_article_id": seo_article.id,
                        "status": "failed",
                        "run_step5": run_step5,
                        "error": f"step5_failed: {str(exc)[:180]}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        article = _publish_seo_article(
            seo_article=seo_article,
            request_user=request.user,
            publish_now=publish_now,
            publish_at=request.data.get("publish_at"),
        )

        return Response(
            {
                "seo_article_id": seo_article.id,
                "article_id": article.id,
                "status": seo_article.status,
                "publish_now": publish_now,
                "publish_at": seo_article.publish_at.isoformat() if seo_article.publish_at else None,
                "run_step5": run_step5,
                "quality": quality_result,
            },
            status=status.HTTP_200_OK,
        )


class LLMApiSettingAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        setting = LLMApiSetting.get_solo()
        serializer = LLMApiSettingSerializer(setting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        setting = LLMApiSetting.get_solo()
        serializer = LLMApiSettingSerializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_by = request.user if request.user and request.user.is_authenticated else None
        serializer.save(updated_by=updated_by)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LLMApiConnectionTestAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = LLMApiConnectionTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        test_result = test_llm_connection(
            base_url=data["base_url"],
            api_key=data["api_key"],
            model=data["model_name"],
            timeout_seconds=data["timeout_seconds"],
        )
        if test_result.get("success"):
            return Response(test_result, status=status.HTTP_200_OK)
        return Response(test_result, status=status.HTTP_400_BAD_REQUEST)


class SeoRewriteAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = SeoRewriteRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        payload = request_serializer.validated_data

        related_game = None
        related_game_id = payload.get("related_game_id")
        if related_game_id:
            related_game = get_object_or_404(GamePage, pk=related_game_id)
        if related_game is None:
            related_game = _resolve_related_game_by_name(payload["game_name"])

        resolved_source_title, resolved_source_url = _build_preferred_source_reference(
            game=related_game,
            game_name=payload["game_name"],
            fallback_title=payload.get("source_title", ""),
            fallback_url=payload.get("source_url", ""),
        )

        rewrite_result = rewrite_bahamut_text(
            raw_text=payload["raw_text"],
            game_name=payload["game_name"],
            keywords=payload.get("keywords"),
        )

        merged_tags = merge_unique_tags(
            base_tags=rewrite_result.get("tags") or [],
            extra_tags=payload.get("keywords") or [],
            limit=12,
        )
        composed_body_html = compose_rich_seo_article_html(
            title=rewrite_result.get("title", ""),
            body_html=rewrite_result.get("body_html", ""),
            game_name=payload["game_name"],
            summary=rewrite_result.get("meta_description", ""),
            keywords=merged_tags,
            search_intent="informational",
            source_title=resolved_source_title or payload.get("source_title", ""),
            source_url=resolved_source_url,
            media_gallery_html="",
            generated_at=timezone.now(),
        )
        composed_body_html = inject_game_internal_link(
            body_html=composed_body_html,
            game_id=related_game.id if related_game else None,
            game_title=related_game.title if related_game else payload["game_name"],
            google_play_id=related_game.google_play_id if related_game else "",
        )
        meta = build_meta_fields(
            title=rewrite_result.get("title", ""),
            body_html=composed_body_html,
            default_title=payload["game_name"],
        )
        standalone_html = build_standalone_seo_html_document(
            title=rewrite_result.get("title", ""),
            meta_description=meta["meta_description"],
            meta_keywords=",".join(merged_tags[:10]),
            body_html=composed_body_html,
        )

        rewrite_result = dict(rewrite_result)
        rewrite_result["body_html"] = composed_body_html
        rewrite_result["tags"] = merged_tags
        rewrite_result["meta_title"] = meta["meta_title"]
        rewrite_result["meta_description"] = meta["meta_description"]

        draft_id = None
        if payload.get("store_draft", True):
            game = related_game
            task = None
            task_id = payload.get("task_id")

            if task_id:
                task = get_object_or_404(CrawlerTask, pk=task_id)

            created_by = request.user if request.user and request.user.is_authenticated else None
            rewrite_payload_for_store = dict(rewrite_result)
            rewrite_payload_for_store["standalone_html"] = standalone_html
            rewrite_payload_for_store["layout"] = {
                "style": "rich_seo_v1",
                "summary_block": True,
                "quick_facts_table": True,
                "metadata_footer": True,
            }
            rewrite_payload_for_store["source_original"] = {
                "title": payload.get("source_title", ""),
                "url": payload.get("source_url", ""),
            }
            rewrite_payload_for_store["source_resolved"] = {
                "title": resolved_source_title or payload.get("source_title", ""),
                "url": resolved_source_url,
            }
            article = SeoArticle.objects.create(
                title=rewrite_result["title"],
                game=game,
                task=task,
                source_title=resolved_source_title or payload.get("source_title", ""),
                source_url=resolved_source_url,
                raw_text=payload["raw_text"],
                body_html=rewrite_result["body_html"],
                tags=rewrite_result["tags"],
                meta_title=rewrite_result.get("meta_title", ""),
                meta_description=rewrite_result["meta_description"],
                rewrite_model=rewrite_result.get("diagnostics", {}).get("model", ""),
                rewrite_payload=rewrite_payload_for_store,
                created_by=created_by,
                status="draft",
            )
            draft_id = article.id

        response_payload = dict(rewrite_result)
        if draft_id is not None:
            response_payload["draft_id"] = draft_id
        response_serializer = SeoRewriteResponseSerializer(data=response_payload)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)



















