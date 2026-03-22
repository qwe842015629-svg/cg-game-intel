import json
import random
import shutil
import re
from datetime import datetime
from html import escape, unescape
from io import BytesIO
from typing import Any
from urllib.parse import quote, urlparse

import requests

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None

from .content_enrichment import (
    build_media_items,
    build_meta_fields,
    compose_rich_seo_article_html,
    merge_unique_tags,
)
from .rewrite import (
    _build_gemini_generate_content_url,
    _build_openai_chat_url,
    _extract_gemini_text,
    _extract_openai_content,
    _post_with_auth_variants,
    _resolve_llm_config,
)

_BING_BLOCKLIST = (
    "bilibili.com",
    "hdslb.com",
    "youtube.com",
    "ytimg.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "pinterest.com",
    "avatar",
    "icon",
    "emoji",
    "sticker",
)

_LINK_BLOCKLIST = (
    "javascript:",
    "data:",
    "vbscript:",
    "home.gamer.com.tw",
    "/comment",
    "/reply",
    "/member/",
)

_HEADING_NOISE_WORDS = (
    "\u524d\u8a00",
    "\u7d50\u8a9e",
    "\u7ed3\u8bed",
    "\u7e3d\u7d50",
    "\u603b\u7ed3",
    "\u4e0b\u8f09",
    "\u4e0b\u8f7d",
    "\u914d\u7f6e",
    "\u9700\u6c42",
    "\u8aaa\u660e",
    "\u8bf4\u660e",
    "\u76ee\u9304",
    "\u76ee\u5f55",
    "faq",
)

_UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

_TEXT_WATERMARK_URL_HINTS = (
    "watermark",
    "logo",
    "caption",
    "subtitle",
    "screenshot",
    "ui",
    "comment",
    "avatar",
    "sticker",
    "thumbnail",
    "thumb",
    "banner",
    "promo",
    "promotion",
    "event",
    "news",
    "forum",
    "giftcode",
    "gift-code",
    "redeem",
    "tier-list",
    "tips",
    "guide",
    "walkthrough",
    "fb",
    "facebook",
    "instagram",
    "tiktok",
    "youtube",
    "discord",
    "telegram",
    "twitter",
    "xhs",
    "xiaohongshu",
    "weibo",
    "ourplay",
    "攻略",
    "\u79ae\u5305\u78bc",
    "\u793c\u5305\u7801",
    "\u514c\u63db\u78bc",
    "\u5151\u6362\u7801",
    "\u6d3b\u52d5",
    "\u6d3b\u52a8",
    "\u516c\u544a",
    "\u60c5\u5831",
    "\u60c5\u62a5",
    "\u6559\u5b78",
    "\u6559\u7a0b",
    "de-games",
    "degames",
)

_NON_GAME_DOMAIN_HINTS = (
    "unsplash.com",
    "pexels.com",
    "pixabay.com",
    "freepik.com",
    "shutterstock.com",
    "istockphoto.com",
    "flickr.com",
)

_GAMING_DOMAIN_HINTS = (
    "gamer.com.tw",
    "steam",
    "game",
    "gaming",
    "nintendo",
    "playstation",
    "xbox",
    "netmarble",
    "mihoyo",
    "hoyoverse",
    "epicgames",
)

_RELEVANCE_GENERIC_TOKENS = {
    "game",
    "games",
    "gaming",
    "mobile",
    "android",
    "ios",
    "guide",
    "tips",
    "tier",
    "list",
    "wiki",
    "news",
    "event",
    "events",
    "official",
    "art",
    "wallpaper",
    "key",
    "visual",
    "cg",
    "screenshot",
    "image",
    "images",
    "video",
    "2024",
    "2025",
    "2026",
}

_CROSS_GAME_HINTS = (
    "genshin",
    "honkai",
    "starrail",
    "star rail",
    "wuthering",
    "wuwa",
    "azurlane",
    "azur lane",
    "arknights",
    "nikke",
    "pubg",
    "freefire",
    "codm",
    "valorant",
    "lol",
    "wild rift",
    "fortnite",
    "apex",
    "clash",
    "royale",
    "brawlstars",
    "fifa",
    "eafc",
)



def run_step5_quality_enhancement(
    *,
    title: str,
    body_html: str,
    game_name: str,
    keywords: list[str] | None = None,
    source_title: str = "",
    source_url: str = "",
    image_seed_urls: list[str] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """
    Step5 quality enhancement:
    1) Clean noisy user traces, keep useful references.
    2) Optional LLM polish with strict anti-noise prompt.
    3) Crawl Bing image candidates and assign one image per H2.
    4) Recompose rich article with inline media.
    """
    normalized_game_name = (game_name or "\u904a\u6232").strip()
    normalized_title = (title or f"{normalized_game_name} \u653b\u7565").strip()
    seed_urls = _dedupe_urls(image_seed_urls or [])

    cleaned_html = _sanitize_body_html(body_html or "")
    polished_html, polish_diag = _polish_with_llm(
        title=normalized_title,
        game_name=normalized_game_name,
        body_html=cleaned_html,
        keywords=keywords or [],
    )
    polished_html = _ensure_minimum_article_shape(
        body_html=polished_html,
        title=normalized_title,
        game_name=normalized_game_name,
    )
    polished_html = _ensure_question_answer_pairs(polished_html, normalized_game_name)
    polished_html = _ensure_on_site_recharge_guidance(polished_html, normalized_game_name)

    h2_sections = _extract_h2_sections(polished_html)
    queries = _build_h2_queries(game_name=normalized_game_name, h2_sections=h2_sections)
    selected_candidates, image_diag = _select_h2_images_from_bing(
        game_name=normalized_game_name,
        h2_sections=h2_sections,
        queries=queries,
        fallback_urls=seed_urls,
    )
    target_image_count = max(1, min(8, len(h2_sections) or 3))
    validated_candidates, validation_diag = _filter_quality_image_candidates(
        _dedupe_candidates(selected_candidates),
        game_name=normalized_game_name,
        limit=target_image_count,
    )
    validation_diag["supplement_checked"] = 0
    validation_diag["supplement_rejected"] = 0
    validation_diag["supplement_kept"] = 0

    if len(validated_candidates) < target_image_count:
        supplement_candidates = _search_bing_images(
            query=f"{normalized_game_name} official game art wallpaper 1280x720",
            max_pages=6,
            per_page_target=64,
        )
        supplement_needed = max(0, target_image_count - len(validated_candidates))
        supplement_validated, supplement_diag = _filter_quality_image_candidates(
            _dedupe_candidates(supplement_candidates),
            game_name=normalized_game_name,
            limit=max(1, supplement_needed),
        )
        validation_diag["supplement_checked"] = int(supplement_diag.get("checked", 0))
        validation_diag["supplement_rejected"] = int(
            supplement_diag.get("rejected_text_or_watermark", 0)
        ) + int(supplement_diag.get("rejected_unreachable", 0)) + int(
            supplement_diag.get("rejected_non_image", 0)
        ) + int(supplement_diag.get("rejected_irrelevant", 0))
        merged_candidates = _merge_selected_candidates(
            base=validated_candidates,
            extra=supplement_validated,
            limit=target_image_count,
        )
        validation_diag["supplement_kept"] = max(0, len(merged_candidates) - len(validated_candidates))
        validated_candidates = merged_candidates

    ordered_candidates = sorted(
        validated_candidates,
        key=lambda item: (
            float(item.get("score") or 0.0),
            float(item.get("relevance_score") or 0.0),
            float(item.get("quality_score") or 0.0),
        ),
        reverse=True,
    )
    selected_urls = [
        str(item.get("url") or "").strip()
        for item in ordered_candidates
        if str(item.get("url") or "").strip()
    ][:target_image_count]
    selected_urls, guarantee_diag = _ensure_real_image_urls(
        selected_urls=selected_urls,
        seed_urls=seed_urls,
        game_name=normalized_game_name,
        target_image_count=target_image_count,
    )
    validation_diag.update(guarantee_diag)

    media_items = build_media_items(
        image_urls=selected_urls,
        game_name=normalized_game_name,
    )

    merged_keywords = merge_unique_tags(
        base_tags=keywords or [],
        extra_tags=[normalized_game_name],
        limit=12,
    )
    summary = _build_step5_summary(polished_html, normalized_game_name)

    final_body_html = compose_rich_seo_article_html(
        title=normalized_title,
        body_html=polished_html,
        game_name=normalized_game_name,
        summary=summary,
        keywords=merged_keywords,
        search_intent="informational",
        source_title=source_title or normalized_title,
        source_url=source_url,
        media_gallery_html="",
        media_items=media_items,
        generated_at=generated_at or datetime.now(),
    )
    meta = build_meta_fields(
        title=normalized_title,
        body_html=final_body_html,
        default_title=normalized_game_name,
    )

    stats = _audit_polished_content(polished_html)
    return {
        "body_html": final_body_html,
        "meta_title": meta["meta_title"],
        "meta_description": meta["meta_description"],
        "selected_images": media_items,
        "cover_image_url": selected_urls[0] if selected_urls else "",
        "diagnostics": {
            "polish": polish_diag,
            "images": {
                **(image_diag if isinstance(image_diag, dict) else {}),
                **validation_diag,
                "target_image_count": target_image_count,
                "validated_selected_count": len(selected_urls),
                "used_placeholder": False,
                "guaranteed_real_image": bool(selected_urls),
                "cover_image_url": selected_urls[0] if selected_urls else "",
            },
            "stats": stats,
            "h2_count": len(h2_sections),
            "selected_image_count": len(media_items),
            "query_count": len(queries),
        },
    }



def _sanitize_body_html(body_html: str) -> str:
    value = str(body_html or "")
    value = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", value)
    value = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", value)
    value = re.sub(r"(?is)<img\b[^>]*>", " ", value)
    value = _sanitize_anchor_tags(value)
    value = _linkify_raw_urls(value)
    value = re.sub(r"(?is)<blockquote\b[^>]*>.*?</blockquote>", " ", value)
    value = _remove_comment_like_paragraphs(value)
    value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
    return value.strip()



def _remove_comment_like_paragraphs(body_html: str) -> str:
    comment_patterns = [
        r"(\u7559\u8a00|\u56de\u8986|\u56de\u590d|\u7db2\u53cb|\u7f51\u53cb|\u6a13\u4e3b|\u697c\u4e3b|\u63a8|\u5653|\u2192|GP|BP)",
        r"(\u4f5c\u8005|\u767c\u4f48\u8005|\u53d1\u5e03\u8005|\u7de8\u8f2f|\u7f16\u8f91|by)\s*[:\uff1a]",
        r"@[\w\u4e00-\u9fff]{2,20}",
    ]
    combined = re.compile("|".join(comment_patterns), flags=re.I)

    def _keep(match: re.Match) -> str:
        block = match.group(0)
        plain = _strip_tags(block)
        if combined.search(plain):
            return ""
        return block

    return re.sub(r"(?is)<p\b[^>]*>.*?</p>", _keep, body_html or "")



def _sanitize_anchor_tags(html_value: str) -> str:
    def _replace(match: re.Match) -> str:
        block = match.group(0)
        inner_html = match.group(1) or ""
        href_match = re.search(r"""href\s*=\s*['\"]([^'\"]+)['\"]""", block, flags=re.I)
        href = str(href_match.group(1) if href_match else "").strip()
        plain_text = _strip_tags(inner_html)
        if not plain_text:
            plain_text = href
        safe_text = escape(plain_text) if plain_text else ""
        if not _is_safe_reference_url(href):
            return safe_text
        safe_href = escape(href, quote=True)
        return (
            f'<a href="{safe_href}" target="_blank" '
            f'rel="noopener noreferrer nofollow">{safe_text}</a>'
        )

    return re.sub(r"(?is)<a\b[^>]*>(.*?)</a>", _replace, html_value or "")



def _linkify_raw_urls(html_value: str) -> str:
    def _replace(match: re.Match) -> str:
        raw_url = str(match.group(1) or "").strip()
        trimmed = raw_url.rstrip(".,;:!?)]}")
        suffix = raw_url[len(trimmed) :]
        if not _is_safe_reference_url(trimmed):
            return suffix
        safe_href = escape(trimmed, quote=True)
        safe_label = escape(trimmed)
        return (
            f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer nofollow">'
            f"{safe_label}</a>{suffix}"
        )

    return re.sub(r"(?<!href=[\"'])(?<![\"'>])(https?://[^\s<>\"]+)", _replace, html_value or "")



def _is_safe_reference_url(url: str) -> bool:
    value = str(url or "").strip()
    if not value:
        return False
    lowered = value.lower()
    if not lowered.startswith(("http://", "https://")):
        return False
    if any(fragment in lowered for fragment in _LINK_BLOCKLIST):
        return False
    return True



def _polish_with_llm(
    *,
    title: str,
    game_name: str,
    body_html: str,
    keywords: list[str],
) -> tuple[str, dict[str, Any]]:
    cfg = _resolve_llm_config()
    api_key = str(cfg.get("api_key") or "").strip()
    if not api_key:
        return body_html, {"enabled": False, "status": "skipped_missing_api_key"}

    prompt = _build_step5_polish_prompt(
        title=title,
        game_name=game_name,
        body_html=body_html,
        keywords=keywords,
    )
    style = str(cfg.get("style") or "openai_chat_completions")
    base_url = str(cfg.get("base_url") or "").strip()
    model = str(cfg.get("model") or "").strip()
    timeout_seconds = int(cfg.get("timeout_seconds") or 45)

    try:
        if style == "gemini_generate_content":
            url = _build_gemini_generate_content_url(base_url=base_url, model=model)
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ]
            }
            response = _post_with_auth_variants(
                url=url,
                payload=payload,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
                prefer_bearer=False,
            )
            response.raise_for_status()
            content = _extract_gemini_text(response.json())
        else:
            url = _build_openai_chat_url(base_url=base_url)
            payload = {
                "model": model,
                "temperature": 0.25,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "\u4f60\u662f\u8cc7\u6df1\u904a\u6232\u7de8\u8f2f\u3002"
                            "\u53ea\u8f38\u51fa JSON\uff0c\u4e0d\u8f38\u51fa\u89e3\u91cb\u3002"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            }
            response = _post_with_auth_variants(
                url=url,
                payload=payload,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
                prefer_bearer=True,
            )
            response.raise_for_status()
            content = _extract_openai_content(response.json())

        parsed = _extract_json_object_safely(content)
        polished_html = str(parsed.get("body_html") or "").strip()
        if not polished_html:
            raise ValueError("empty_body_html")
        polished_html = _sanitize_body_html(polished_html)
        return polished_html, {
            "enabled": True,
            "status": "completed",
            "style": style,
            "model": model,
        }
    except Exception as exc:
        return body_html, {
            "enabled": True,
            "status": "fallback",
            "reason": str(exc)[:180],
            "style": style,
            "model": model,
        }



def _build_step5_polish_prompt(
    *,
    title: str,
    game_name: str,
    body_html: str,
    keywords: list[str],
) -> str:
    preferred_keywords = "\u3001".join((keywords or [])[:12]) or game_name
    return (
        "\u7e7c\u7e8c\u512a\u5316\u6587\u7ae0\uff0c\u53bb\u6389\u73a9\u5bb6\u59d3\u540d\u8207\u7559\u8a00\u75d5\u8de1\uff0c\u4ee5\u53ca\u5716\u7247\u4e2d\u7684\u7121\u95dc\u5167\u5bb9\uff0c"
        "\u8f38\u51fa\u50cf\u771f\u4eba\u73a9\u5bb6\u64b0\u5beb\u7684\u81ea\u7136\u5167\u5bb9\u3002\n"
        "\u8acb\u56b4\u683c\u57f7\u884c\uff1a\n"
        "1) \u5168\u6587\u4f7f\u7528\u53f0\u7063\u7e41\u9ad4\u4e2d\u6587\uff0c\u8a9e\u6c23\u53e3\u8a9e\u5316\uff0c\u4fdd\u7559\u904a\u6232\u8cc7\u8a0a\u8207\u5be6\u7528\u5efa\u8b70\u3002\n"
        "2) \u522a\u9664\u73a9\u5bb6\u66b1\u7a31\u3001\u8ad6\u58c7\u7559\u8a00/\u56de\u8986\u75d5\u8de1\u3001\u7121\u95dc\u5f15\u6230\u5167\u5bb9\u3002\n"
        "3) \u4fdd\u7559\u6709\u50f9\u503c\u7684\u8cc7\u6599\u4f86\u6e90\u9023\u7d50\uff1b\u79fb\u9664\u500b\u4eba\u4e3b\u9801\u3001\u8a55\u8ad6\u5340\u3001\u7121\u95dc\u5ee3\u544a\u9023\u7d50\u3002\n"
        "4) \u522a\u9664\u6240\u6709\u5716\u7247\u6a19\u7c64\uff0c\u7531\u5f8c\u7e8c\u6d41\u7a0b\u91cd\u65b0\u914d\u5716\u3002\n"
        "5) body_html \u5fc5\u9808\u662f HTML \u7247\u6bb5\uff0c\u4e0d\u8981\u5305\u542b <html>/<head>/<body>/<style>/<script>\u3002\n"
        "6) \u4fdd\u7559 1 \u500b <h1>\u3001\u81f3\u5c11 3 \u500b <h2>\uff0c\u4e26\u4fdd\u6301\u6bb5\u843d\u53ef\u8b80\u3002\n"
        "7) \u6a19\u984c/\u5c0f\u6a19/\u5167\u6587\u907f\u514d\u4ee5\u4e0b\u8a5e\uff1a\u5168\u65b9\u4f4d\u3001\u89e3\u6790\u3001\u5168\u9762\u3001\u6307\u5357\u3001\u9ad8\u6548\u3002\n"
        "8) \u5217\u9ede\u689d\u76ee\u8acb\u4f7f\u7528 emoji \u4f5c\u70ba\u9805\u76ee\u7b26\u865f\uff08\u4f8b\u5982 \u2728/\U0001F3AF/\U0001F9ED/\U0001F6E1\ufe0f\uff09\uff0c\u4fdd\u6301\u8f15\u9b06\u8b80\u611f\u3002\n"
        "9) \u82e5\u4f7f\u7528 Q/A \u5f62\u5f0f\uff0c\u6bcf\u500b Q \u5fc5\u9808\u6709\u5c0d\u61c9\u7684 A\uff0c\u4e0d\u53ef\u55ae\u7368\u7559\u4e0b\u554f\u984c\u3002\n"
        "10) \u6d89\u53ca\u5132\u503c/\u5145\u503c\u6bb5\u843d\u6642\uff0c\u8acb\u7528\u81ea\u7136\u5206\u4eab\u53e3\u543b\u63d0\u9192\u300c\u53ef\u5728\u672c\u7ad9\u5c0d\u61c9\u904a\u6232\u9801\u5b8c\u6210\u64cd\u4f5c\u300d\uff0c\u4e0d\u53ef\u7528\u5f37\u63a8\u92b7\u552e\u8a9e\u6c23\u3002\n"
        "11) \u4e0d\u8981\u8f38\u51fa\u4efb\u4f55\u89e3\u91cb\uff0c\u53ea\u8f38\u51fa JSON\uff1a{\"body_html\":\"...\"}\n\n"
        f"\u6587\u7ae0\u6a19\u984c\uff1a{title}\n"
        f"\u904a\u6232\u540d\u7a31\uff1a{game_name}\n"
        f"\u95dc\u9375\u8a5e\uff1a{preferred_keywords}\n"
        f"\u539f\u59cb\u6b63\u6587\uff1a\n{body_html}"
    )



def _extract_json_object_safely(raw_text: str) -> dict[str, Any]:
    text = str(raw_text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        parsed = json.loads(text[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("invalid_json_from_llm")



def _ensure_minimum_article_shape(*, body_html: str, title: str, game_name: str) -> str:
    html = str(body_html or "").strip()
    if not html:
        html = f"<h1>{escape(title)}</h1><p>{escape(game_name)} \u653b\u7565\u5167\u5bb9\u5f85\u88dc\u5145\u3002</p>"

    if not re.search(r"(?is)<h1\b[^>]*>.*?</h1>", html):
        html = f"<h1>{escape(title)}</h1>" + html

    h2_count = len(re.findall(r"(?is)<h2\b[^>]*>.*?</h2>", html))
    if h2_count < 3:
        html += (
            "<h2>\u73a9\u6cd5\u91cd\u9ede\u6574\u7406</h2>"
            "<p>\u5148\u78ba\u8a8d\u7248\u672c\u76ee\u6a19\u8207\u7dc3\u5ea6\u65b9\u5411\uff0c\u518d\u8abf\u6574\u8cc7\u6e90\u6295\u5165\u9806\u5e8f\uff0c\u53ef\u4ee5\u907f\u514d\u8d70\u5197\u8def\u3002</p>"
            "<h2>\u5132\u503c\u8207\u5b89\u5168\u63d0\u9192</h2>"
            "<p>\u5132\u503c\u524d\u5148\u6838\u5c0d\u4f3a\u670d\u5668\u3001\u89d2\u8272\u8207\u5546\u54c1\u9762\u984d\uff0c\u4fdd\u7559\u8a02\u55ae\u61d1\u8b49\uff0c\u78ba\u4fdd\u4ea4\u6613\u5b89\u5168\u3002</p>"
            "<h2>\u5e38\u898b\u554f\u984c</h2>"
            "<h3>\u65b0\u624b\u5148\u505a\u4ec0\u9ebc\uff1f</h3>"
            "<p>\u5148\u5b8c\u6210\u4e3b\u7dda\u8207\u9ad8\u56de\u5831\u4efb\u52d9\uff0c\u6703\u6bd4\u4e00\u958b\u59cb\u5c31\u5e7f\u6492\u8cc7\u6e90\u66f4\u7a69\u3002</p>"
            "<h3>\u5c6c\u6027\u600e\u9ebc\u5806\u6bd4\u8f03\u4e0d\u6703\u6b6a\uff1f</h3>"
            "<p>\u4f9d\u7167\u7576\u524d\u7248\u672c\u4e3b\u6d41\u914d\u88dd\u8abf\u6574\uff0c\u4e0d\u8981\u4e00\u6b21\u5206\u6563\u5728\u592a\u591a\u652f\u7dda\u4e0a\u3002</p>"
        )

    plain_len = len(_strip_tags(html))
    if plain_len < 900:
        html += (
            "<h2>\u9032\u968e\u5beb\u6cd5\u8207\u7bc0\u594f\u5efa\u8b70</h2>"
            "<p>\u5be6\u969b\u73a9\u8d77\u4f86\uff0c\u5efa\u8b70\u5148\u8a02\u51fa\u6bcf\u9031\u76ee\u6a19\uff0c\u4f8b\u5982\u300c\u4e3b\u529b\u89d2\u8272\u63d0\u5347\u300d\u3001\u300c\u95dc\u9375\u526f\u672c\u6e05\u7a7a\u300d\u3001\u300c\u6d3b\u52d5\u514c\u63db\u8cc7\u6e90\u5403\u6eff\u300d\u3002"
            "\u9019\u6a23\u4f60\u5728\u6bcf\u5929\u767b\u5165\u6642\uff0c\u5c31\u80fd\u5feb\u901f\u5224\u65b7\u73fe\u5728\u8a72\u5148\u505a\u4ec0\u9ebc\uff0c\u4e0d\u6703\u88ab\u96f6\u788e\u4e8b\u60c5\u6253\u4e82\u3002"
            "\u53e6\u5916\uff0c\u8cc7\u6e90\u6295\u5165\u63a8\u85a6\u7528\u300c\u4e3b\u8ef8 + \u5099\u63f4\u300d\u7684\u601d\u8def\uff0c\u4e3b\u8ef8\u5148\u9924\u98fd\uff0c\u5099\u63f4\u518d\u88dc\u4f4d\uff0c\u5c31\u80fd\u540c\u6642\u9867\u5230\u958b\u8352\u6548\u7387\u548c\u5f8c\u671f\u6210\u9577\u3002</p>"
            "<p>\u5982\u679c\u4f60\u73a9\u7684\u6642\u9593\u6bd4\u8f03\u788e\uff0c\u53ef\u4ee5\u628a\u300c\u81ea\u52d5\u5faa\u74b0\u4efb\u52d9\u300d\u8207\u300c\u9ad8\u56de\u5831\u4efb\u52d9\u300d\u62c6\u958b\u8655\u7406\uff1a"
            "\u5e73\u65e5\u5148\u628a\u4fdd\u5e95\u9032\u5ea6\u505a\u5b8c\uff0c\u9031\u672b\u518d\u96c6\u4e2d\u6253\u8f03\u82b1\u6642\u9593\u7684\u5167\u5bb9\uff0c\u6574\u9ad4\u9ad4\u9a57\u6703\u9806\u5f88\u591a\u3002"
            "\u9019\u4e5f\u662f\u5f88\u591a\u8001\u73a9\u5bb6\u9577\u671f\u7a69\u5b9a\u6210\u9577\u7684\u95dc\u9375\u65b9\u5f0f\u3002</p>"
        )

    if "<table" not in html.lower():
        html += (
            "<h2>\u6574\u7406\u5c0f\u8868\u683c</h2>"
            "<table><thead><tr><th>\u9805\u76ee</th><th>\u5efa\u8b70</th></tr></thead><tbody>"
            "<tr><td>\u6bcf\u65e5\u512a\u5148\u5ea6</td><td>\u4e3b\u7dda\u8207\u9ad8\u56de\u5831\u4efb\u52d9\u5148\u505a\u5b8c</td></tr>"
            "<tr><td>\u8cc7\u6e90\u5206\u914d</td><td>\u5148\u9924\u98fd\u4e3b\u529b\u89d2\u8272\uff0c\u518d\u88dc\u5099\u63f4\u7dda</td></tr>"
            "<tr><td>\u5132\u503c\u6d41\u7a0b</td><td>\u4ed8\u6b3e\u524d\u518d\u6b21\u6838\u5c0d\u4f3a\u670d\u5668\u8207\u89d2\u8272\u8cc7\u8a0a</td></tr>"
            "</tbody></table>"
        )

    return html



def _extract_h2_sections(body_html: str) -> list[dict[str, str]]:
    html = str(body_html or "")
    matches = list(re.finditer(r"(?is)<h2\b[^>]*>(.*?)</h2>", html))
    if not matches:
        return []

    sections: list[dict[str, str]] = []
    for idx, match in enumerate(matches):
        heading_html = match.group(1) or ""
        heading = _strip_tags(heading_html).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(html)
        content_html = html[start:end]
        content = _strip_tags(content_html).strip()
        sections.append(
            {
                "heading": heading,
                "content": content,
            }
        )
    return sections



def _build_h2_queries(*, game_name: str, h2_sections: list[dict[str, str]]) -> list[str]:
    queries: list[str] = []
    for section in h2_sections:
        heading = str(section.get("heading") or "").strip()
        if not heading:
            continue
        normalized_heading = heading
        for noise in _HEADING_NOISE_WORDS:
            normalized_heading = normalized_heading.replace(noise, "")
        normalized_heading = re.sub(r"[：:|｜\-—_]+", " ", normalized_heading)
        normalized_heading = re.sub(r"\s+", " ", normalized_heading).strip()
        if not normalized_heading:
            normalized_heading = heading
        queries.append(f"{game_name} {normalized_heading} wallpaper game official art 1280x720")
    return queries



def _select_h2_images_from_bing(
    *,
    game_name: str,
    h2_sections: list[dict[str, str]],
    queries: list[str],
    fallback_urls: list[str],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if not h2_sections:
        selected = [
            {"url": value, "title": "", "query": "", "source": "seed"}
            for value in _dedupe_urls(fallback_urls)[:1]
        ]
        return selected, {
            "status": "no_h2",
            "queries": [],
            "candidate_count": 0,
            "source": "fallback_only",
        }

    all_candidates: list[dict[str, str]] = []
    for query in queries:
        candidates = _search_bing_images(query=query, max_pages=4, per_page_target=24)
        all_candidates.extend(candidates)

    if not all_candidates:
        all_candidates.extend(
            _search_bing_images(
                query=f"{game_name} game wallpaper official art 1280x720",
                max_pages=6,
                per_page_target=40,
            )
        )

    dedup_candidates = _dedupe_candidates(all_candidates)
    selected_items: list[dict[str, str]] = []
    used_urls: set[str] = set()

    for section_idx, section in enumerate(h2_sections):
        heading = str(section.get("heading") or "")
        content = str(section.get("content") or "")
        ranked = sorted(
            dedup_candidates,
            key=lambda item: _score_candidate(
                item=item,
                game_name=game_name,
                heading=heading,
                content=content,
            ),
            reverse=True,
        )
        chosen_item: dict[str, str] | None = None
        for item in ranked:
            url = str(item.get("url") or "").strip()
            if not url or url in used_urls:
                continue
            chosen_item = {
                "url": url,
                "title": str(item.get("title") or ""),
                "query": str(item.get("query") or ""),
                "source": "bing",
                "heading": heading,
                "section_index": str(section_idx),
            }
            break
        if chosen_item:
            used_urls.add(chosen_item["url"])
            selected_items.append(chosen_item)

    for url in _dedupe_urls(fallback_urls):
        if len(selected_items) >= len(h2_sections):
            break
        if url in used_urls:
            continue
        used_urls.add(url)
        selected_items.append(
            {
                "url": url,
                "title": "",
                "query": "",
                "source": "seed",
            }
        )

    return selected_items, {
        "status": "completed" if selected_items else "fallback_or_empty",
        "queries": queries,
        "candidate_count": len(dedup_candidates),
        "selected_count": len(selected_items),
        "h2_count": len(h2_sections),
    }



def _search_bing_images(*, query: str, max_pages: int = 4, per_page_target: int = 24) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    encoded_query = quote(query)
    headers = {
        "User-Agent": random.choice(_UA_POOL),
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.bing.com/",
    }

    for page in range(max_pages):
        first = page * 35
        url = (
            "https://www.bing.com/images/search"
            f"?q={encoded_query}&qft=+filterui:imagesize-large&first={first}"
        )
        try:
            response = requests.get(url, headers=headers, timeout=(10, 18))
            response.raise_for_status()
        except Exception:
            continue

        page_candidates = _parse_bing_candidates(response.text)
        page_added = 0
        for item in page_candidates:
            image_url = str(item.get("url") or "").strip()
            if not image_url or image_url in seen_urls:
                continue
            lower = image_url.lower()
            if any(blocked in lower for blocked in _BING_BLOCKLIST):
                continue
            seen_urls.add(image_url)
            page_added += 1
            candidates.append(
                {
                    "url": image_url,
                    "title": str(item.get("title") or ""),
                    "query": query,
                }
            )

        if page_added == 0 and page > 1:
            break
        if len(candidates) >= per_page_target:
            break

    return candidates



def _parse_bing_candidates(html_text: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    if not html_text:
        return results

    for raw_m in re.findall(r'(?is)class="[^"]*iusc[^"]*"[^>]*\sm="([^"]+)"', html_text):
        payload_text = unescape(raw_m)
        try:
            data = json.loads(payload_text)
        except Exception:
            continue
        image_url = str(data.get("murl") or data.get("turl") or "").strip()
        if not image_url.startswith("http"):
            continue
        results.append(
            {
                "url": image_url,
                "title": str(data.get("t") or data.get("desc") or ""),
            }
        )

    for image_url in re.findall(r'(?is)"murl":"(https?:\\/\\/[^\"]+)"', html_text):
        normalized_url = image_url.replace("\\/", "/").strip()
        if normalized_url.startswith("http"):
            results.append({"url": normalized_url, "title": ""})

    return results



def _score_candidate(*, item: dict[str, str], game_name: str, heading: str, content: str) -> float:
    url = str(item.get("url") or "").strip().lower()
    title = str(item.get("title") or "").strip().lower()
    source = str(item.get("source") or "").strip().lower()
    text = " ".join([title, url])
    host = _host_from_url(url)
    score = 0.0

    game_tokens = _tokenize_for_match(game_name)
    game_hit = sum(1 for token in game_tokens[:8] if token and token in text)
    if game_hit > 0:
        score += 10.0 + (2.2 * game_hit)
    elif source != "seed":
        score -= 6.0

    for token in _tokenize_for_match(heading)[:10]:
        if token and token in text:
            score += 3.0
    for token in _tokenize_for_match(content)[:12]:
        if token and token in text:
            score += 1.0

    if source == "seed":
        score += 8.0

    if any(hint in host for hint in _GAMING_DOMAIN_HINTS):
        score += 6.0
    if any(hint in host for hint in _NON_GAME_DOMAIN_HINTS):
        score -= 8.0

    if any(word in text for word in ("wallpaper", "official art", "key visual", "screenshot", "cg")):
        score += 2.5
    if any(word in text for word in ("portrait", "fashion", "makeup", "model", "street style")):
        score -= 6.0
    if any(noise in text for noise in ("icon", "logo", "avatar", "emoji", "sticker")):
        score -= 5.0

    return float(score)


def _host_from_url(url: str) -> str:
    try:
        return str(urlparse(url).netloc or "").lower()
    except Exception:
        return ""



def _build_placeholder_urls(*, game_name: str, h2_sections: list[dict[str, str]], fallback_count: int) -> list[str]:
    urls: list[str] = []
    if h2_sections:
        for section in h2_sections:
            heading = str(section.get("heading") or "NEWS").strip()
            urls.append(_build_svg_data_url(game_name=game_name, heading=heading))
        return _dedupe_urls(urls)

    for index in range(max(1, fallback_count)):
        urls.append(_build_svg_data_url(game_name=game_name, heading=f"NEWS {index + 1}"))
    return _dedupe_urls(urls)



def _build_svg_data_url(*, game_name: str, heading: str) -> str:
    safe_game = re.sub(r"[<>]", "", str(game_name or "\u904a\u6232")).strip()[:24]
    safe_heading = re.sub(r"[<>]", "", str(heading or "NEWS")).strip()[:24]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">'
        '<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1">'
        '<stop offset="0%" stop-color="#e8f0ff"/><stop offset="100%" stop-color="#d5e6ff"/>'
        '</linearGradient></defs>'
        '<rect width="1200" height="675" fill="url(#g)"/>'
        '<rect x="72" y="72" width="1056" height="531" rx="24" fill="#ffffff" opacity="0.85"/>'
        f'<text x="600" y="300" text-anchor="middle" font-size="52" fill="#1f3b6d" font-family="Segoe UI, Microsoft JhengHei, sans-serif">{escape(safe_game)}</text>'
        f'<text x="600" y="370" text-anchor="middle" font-size="34" fill="#2c5f9e" font-family="Segoe UI, Microsoft JhengHei, sans-serif">{escape(safe_heading)}</text>'
        '<text x="600" y="430" text-anchor="middle" font-size="24" fill="#5f7ea8" font-family="Segoe UI, Microsoft JhengHei, sans-serif">NEWS</text>'
        '</svg>'
    )
    return "data:image/svg+xml;utf8," + quote(svg, safe="/:?&=,+-._~@#")



def _tokenize_for_match(text: str) -> list[str]:
    raw = re.sub(r"<[^>]+>", " ", str(text or ""))
    raw = re.sub(r"\s+", " ", raw).strip().lower()
    tokens = re.findall(r"[a-z0-9\u4e00-\u9fff]{2,20}", raw)
    seen: set[str] = set()
    result: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result



def _strip_tags(value: str) -> str:
    text = re.sub(r"(?is)<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()



def _first_paragraph_text(body_html: str) -> str:
    match = re.search(r"(?is)<p[^>]*>(.*?)</p>", body_html or "")
    if match:
        return _strip_tags(match.group(1))[:260]
    return _strip_tags(body_html)[:260]


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[。！？!?])|[\n\r]+", str(text or ""))
    output: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        item = _strip_tags(chunk)
        if len(item) < 8:
            continue
        key = re.sub(r"\s+", "", item)
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def _build_step5_summary(body_html: str, game_name: str) -> str:
    headings = [
        _strip_tags(value)
        for value in re.findall(r"(?is)<h2\b[^>]*>(.*?)</h2>", body_html or "")
    ]
    headings = [value for value in headings if value][:3]
    sentences = _split_sentences(_strip_tags(body_html))
    first_sentence = sentences[0] if sentences else ""
    second_sentence = sentences[1] if len(sentences) > 1 else ""

    parts: list[str] = []
    if headings:
        parts.append(f"本文聚焦 {game_name} 的{'、'.join(headings)}。")
    if first_sentence:
        parts.append(first_sentence)
    if second_sentence and second_sentence != first_sentence:
        parts.append(second_sentence)

    summary = _strip_tags(" ".join(parts))
    if not summary:
        summary = f"本文整理 {game_name} 的版本重點、實戰技巧與儲值安全注意事項。"
    return summary[:260]


def _ensure_question_answer_pairs(body_html: str, game_name: str) -> str:
    html = str(body_html or "")
    answer_tpl = (
        "<p>A{num}：建議先依照 {game} 當前版本主流配置調整，"
        "並在投入資源前完成區服、角色與商品資訊核對，通常就能避免大多數風險。</p>"
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



def repair_article_section_completeness(*, body_html: str, game_name: str) -> str:
    # Backward-compatible entry point used by older seo_automation views.
    _ = game_name
    return str(body_html or "")


def _ensure_on_site_recharge_guidance(body_html: str, game_name: str) -> str:
    html = str(body_html or "")
    plain = _strip_tags(html)
    plain_lower = plain.lower()
    has_site_text = any(token in plain for token in ("\u672c\u7ad9", "\u672c\u7db2\u7ad9"))
    has_recharge_text = any(token in plain for token in ("\u5132\u503c", "\u5145\u503c", "\u88dc\u8ca8"))
    if has_site_text and has_recharge_text:
        return html
    if "\u7ad9\u5167\u64cd\u4f5c\u63d0\u9192" in plain:
        return html
    if "recharge" in plain_lower and "site" in plain_lower:
        return html

    guidance_html = (
        f"<h2>{escape(game_name)} \u7ad9\u5167\u64cd\u4f5c\u63d0\u9192</h2>"
        "<p>\u9700\u8981\u88dc\u8db3\u8cc7\u6e90\u6642\uff0c\u53ef\u4ee5\u76f4\u63a5\u5728\u672c\u7ad9\u7684\u5c0d\u61c9\u904a\u6232\u9801\u9762\u5b8c\u6210\u5132\u503c\u8207\u8a02\u55ae\u67e5\u6838\uff0c"
        "\u9019\u6a23\u53ef\u4ee5\u907f\u514d\u5728\u591a\u500b\u7db2\u9801\u4f86\u56de\u5207\u63db\uff0c\u4e5f\u66f4\u65b9\u4fbf\u5f8c\u7e8c\u5c0d\u5e33\u3002</p>"
    )
    return html + guidance_html


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in urls or []:
        item = str(raw or "").strip()
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result



def _dedupe_candidates(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in items or []:
        url = str(item.get("url") or "").strip()
        key = _url_dedupe_key(url)
        if not url or not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result



def _ensure_real_image_urls(
    *,
    selected_urls: list[str],
    seed_urls: list[str],
    game_name: str,
    target_image_count: int,
) -> tuple[list[str], dict[str, int | str]]:
    target = max(1, int(target_image_count or 1))
    kept_urls: list[str] = []
    for raw in _dedupe_urls(selected_urls or []):
        if _is_acceptable_real_image_url(raw):
            kept_urls.append(raw)
        if len(kept_urls) >= target:
            break

    diag: dict[str, int | str] = {
        "emergency_seed_fallback": 0,
        "guarantee_source": "validated_candidates" if kept_urls else "none",
        "guarantee_added_count": 0,
    }
    if kept_urls:
        return kept_urls, diag

    seed_pool = [url for url in _dedupe_urls(seed_urls or []) if _is_acceptable_real_image_url(url)]
    http_seed_pool = [url for url in seed_pool if url.lower().startswith(("http://", "https://"))]
    local_seed_pool = [url for url in seed_pool if not url.lower().startswith(("http://", "https://"))]

    if http_seed_pool:
        seed_candidates = [{"url": url, "source": "seed"} for url in http_seed_pool]
        validated_seed, _seed_diag = _filter_quality_image_candidates(
            seed_candidates,
            game_name=game_name,
            limit=target,
            max_checked=max(80, min(220, target * 60)),
        )
        for item in validated_seed:
            value = str(item.get("url") or "").strip()
            if value and value not in kept_urls:
                kept_urls.append(value)
            if len(kept_urls) >= target:
                break
        if kept_urls:
            diag["emergency_seed_fallback"] = len(kept_urls)
            diag["guarantee_source"] = "seed_validated"
            diag["guarantee_added_count"] = len(kept_urls)
            return kept_urls, diag

    if local_seed_pool:
        for value in local_seed_pool:
            if value and value not in kept_urls:
                kept_urls.append(value)
            if len(kept_urls) >= target:
                break
        if kept_urls:
            diag["emergency_seed_fallback"] = len(kept_urls)
            diag["guarantee_source"] = "seed_local"
            diag["guarantee_added_count"] = len(kept_urls)
            return kept_urls, diag

    aggressive_queries = [
        f"{game_name} official game key visual",
        f"{game_name} game wallpaper 1920x1080",
        f"{game_name} gameplay screenshot",
        f"{game_name} character art",
    ]
    aggressive_candidates: list[dict[str, str]] = []
    for query in aggressive_queries:
        aggressive_candidates.extend(
            _search_bing_images(
                query=query,
                max_pages=8,
                per_page_target=80,
            )
        )
    if aggressive_candidates:
        validated_fallback, _fallback_diag = _filter_quality_image_candidates(
            _dedupe_candidates(aggressive_candidates),
            game_name=game_name,
            limit=target,
            max_checked=240,
        )
        for item in validated_fallback:
            value = str(item.get("url") or "").strip()
            if value and value not in kept_urls:
                kept_urls.append(value)
            if len(kept_urls) >= target:
                break
        if kept_urls:
            diag["guarantee_source"] = "bing_aggressive"
            diag["guarantee_added_count"] = len(kept_urls)
            return kept_urls, diag

    return kept_urls, diag


def _is_acceptable_real_image_url(value: str) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    if lowered.startswith(("data:", "javascript:", "vbscript:")):
        return False
    return True

def _filter_quality_image_candidates(
    candidates: list[dict[str, Any]] | list[str],
    *,
    game_name: str,
    limit: int = 8,
    max_checked: int = 80,
) -> tuple[list[dict[str, Any]], dict[str, int | str | float]]:
    checked = 0
    scanned = 0
    normalized_candidates = _normalize_candidate_pool(candidates or [])
    rejected_text_or_watermark = 0
    rejected_unreachable = 0
    rejected_non_image = 0
    rejected_irrelevant = 0
    rejected_duplicate = 0
    seen_url_keys: set[str] = set()
    scored: list[dict[str, Any]] = []

    for item in normalized_candidates:
        if scanned >= max(1, int(max_checked or 1)):
            break
        scanned += 1

        url = str(item.get("url") or "").strip()
        if not url:
            continue
        url_key = _url_dedupe_key(url)
        if not url_key or url_key in seen_url_keys:
            continue
        seen_url_keys.add(url_key)
        checked += 1

        image_bytes, content_type, fetch_status = _fetch_image_bytes(url)
        if fetch_status == "non_image":
            rejected_non_image += 1
            continue
        if fetch_status != "ok" or not image_bytes:
            rejected_unreachable += 1
            continue

        should_reject, _reason = _reject_image_by_text_or_watermark(
            image_bytes=image_bytes,
            image_url=url,
        )
        if should_reject:
            rejected_text_or_watermark += 1
            continue

        source = str(item.get("source") or "").strip().lower()
        relevance_score = _score_candidate_relevance(
            candidate=item,
            game_name=game_name,
        )
        min_relevance = 0.34 if source == "seed" else 0.42
        if relevance_score < min_relevance:
            rejected_irrelevant += 1
            continue

        quality_metrics = _estimate_image_quality_metrics(image_bytes)
        quality_score = float(quality_metrics.get("quality_score") or 0.0)
        final_score = (relevance_score * 0.72) + (quality_score * 0.28)

        scored.append(
            {
                **item,
                "url": url,
                "source": source or "bing",
                "relevance_score": round(relevance_score, 4),
                "quality_score": round(quality_score, 4),
                "score": round(final_score, 4),
                "image_hash": _build_dhash(image_bytes),
                "width": int(quality_metrics.get("width") or 0),
                "height": int(quality_metrics.get("height") or 0),
            }
        )

    scored.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    selected: list[dict[str, Any]] = []
    selected_hashes: list[str] = []
    limit_value = max(1, int(limit or 1))
    for item in scored:
        if len(selected) >= limit_value:
            break
        hash_value = str(item.get("image_hash") or "").strip()
        if hash_value and _is_similar_hash(hash_value, selected_hashes):
            rejected_duplicate += 1
            continue
        selected.append(item)
        if hash_value:
            selected_hashes.append(hash_value)

    ocr_backend = "none"
    if pytesseract is not None and Image is not None and shutil.which("tesseract"):
        ocr_backend = "pytesseract"

    top_score = float(selected[0].get("score") or 0.0) if selected else 0.0
    return selected, {
        "checked": checked,
        "scanned": scanned,
        "kept": len(selected),
        "rejected_text_or_watermark": rejected_text_or_watermark,
        "rejected_unreachable": rejected_unreachable,
        "rejected_non_image": rejected_non_image,
        "rejected_irrelevant": rejected_irrelevant,
        "rejected_duplicate": rejected_duplicate,
        "min_relevance_non_seed": 0.42,
        "min_relevance_seed": 0.34,
        "ocr_backend": ocr_backend,
        "top_score": round(top_score, 4),
    }


def _normalize_candidate_pool(candidates: list[dict[str, Any]] | list[str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for raw in candidates or []:
        if isinstance(raw, dict):
            url = str(raw.get("url") or "").strip()
            title = str(raw.get("title") or "").strip()
            query = str(raw.get("query") or "").strip()
            source = str(raw.get("source") or "").strip() or "bing"
            heading = str(raw.get("heading") or "").strip()
        else:
            url = str(raw or "").strip()
            title = ""
            query = ""
            source = "seed"
            heading = ""
        if not url:
            continue
        result.append(
            {
                "url": url,
                "title": title,
                "query": query,
                "source": source,
                "heading": heading,
            }
        )
    return result


def _merge_selected_candidates(
    *,
    base: list[dict[str, Any]],
    extra: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen_url_keys: set[str] = set()
    seen_hashes: list[str] = []
    limit_value = max(1, int(limit or 1))

    for item in [*(base or []), *(extra or [])]:
        if len(merged) >= limit_value:
            break
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        key = _url_dedupe_key(url)
        if not key or key in seen_url_keys:
            continue
        image_hash = str(item.get("image_hash") or "").strip()
        if image_hash and _is_similar_hash(image_hash, seen_hashes):
            continue

        seen_url_keys.add(key)
        merged.append(item)
        if image_hash:
            seen_hashes.append(image_hash)
    return merged


def _url_dedupe_key(url: str) -> str:
    value = str(url or "").strip()
    if not value:
        return ""
    try:
        parsed = urlparse(value)
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").rstrip("/")
        return f"{host}{path}".lower()
    except Exception:
        return value.lower().split("?", 1)[0]


def _score_candidate_relevance(*, candidate: dict[str, Any], game_name: str) -> float:
    source = str(candidate.get("source") or "").strip().lower()

    url = str(candidate.get("url") or "").strip().lower()
    title = str(candidate.get("title") or "").strip().lower()
    heading = str(candidate.get("heading") or "").strip().lower()
    query = str(candidate.get("query") or "").strip().lower()
    host = _host_from_url(url)
    title_url_text = " ".join([title, url])
    context_text = " ".join([title_url_text, query])
    score = 0.0

    game_tokens = [
        token
        for token in _tokenize_for_match(game_name)[:10]
        if token and token not in _RELEVANCE_GENERIC_TOKENS
    ]
    strong_hits = sum(1 for token in game_tokens if token in title_url_text)
    context_hits = sum(1 for token in game_tokens if token in context_text)
    if strong_hits > 0:
        score += min(0.62, (0.22 + (0.16 * strong_hits)))
    elif context_hits > 0:
        score += min(0.16, 0.05 * context_hits)
        score -= 0.16
    else:
        score -= 0.28

    heading_tokens = [
        token
        for token in _tokenize_for_match(heading)[:8]
        if token and token not in _RELEVANCE_GENERIC_TOKENS
    ]
    if heading_tokens:
        heading_hits = sum(1 for token in heading_tokens if token in title_url_text)
        if heading_hits > 0:
            score += min(0.16, 0.06 * heading_hits)
        else:
            score -= 0.08

    query_tokens = [
        token
        for token in _tokenize_for_match(query)[:12]
        if token and token not in _RELEVANCE_GENERIC_TOKENS
    ]
    if query_tokens:
        query_focus_tokens = [token for token in query_tokens if token not in game_tokens]
        if query_focus_tokens:
            query_hits = sum(1 for token in query_focus_tokens if token in title_url_text)
            if query_hits > 0:
                score += min(0.1, 0.03 * query_hits)
            else:
                score -= 0.07

    if source == "seed":
        score += 0.08 if strong_hits > 0 else -0.03

    if any(hint in host for hint in _GAMING_DOMAIN_HINTS):
        score += 0.14
    if any(hint in host for hint in _NON_GAME_DOMAIN_HINTS):
        score -= 0.32

    if any(noise in context_text for noise in ("portrait", "fashion", "makeup", "model", "street style")):
        score -= 0.28
    if any(
        noise in context_text
        for noise in ("icon", "logo", "avatar", "emoji", "sticker", "thumbnail", "thumb")
    ):
        score -= 0.28
    if any(
        noise in context_text
        for noise in ("gift code", "giftcode", "redeem", "coupon", "promo", "promotion", "tier list")
    ):
        score -= 0.2
    if any(
        word in context_text
        for word in ("wallpaper", "official art", "key visual", "screenshot", "cg", "splash art", "character art")
    ):
        score += 0.1

    lowered_game_name = str(game_name or "").lower()
    if strong_hits <= 0 and any(
        hint in context_text and hint not in lowered_game_name
        for hint in _CROSS_GAME_HINTS
    ):
        score -= 0.24

    return max(0.0, min(1.0, score + 0.24))


def _estimate_image_quality_metrics(image_bytes: bytes) -> dict[str, float | int]:
    if not image_bytes or Image is None:
        return {"quality_score": 0.0, "width": 0, "height": 0}
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return {"quality_score": 0.0, "width": 0, "height": 0}

    width, height = image.size
    area = max(1, width * height)
    aspect = width / max(1, height)
    target_aspect = 16 / 9
    aspect_score = max(0.0, 1.0 - min(1.0, abs(aspect - target_aspect) / 1.35))
    resolution_score = min(1.0, area / float(1600 * 900))

    gray = image.convert("L")
    gray.thumbnail((840, 840))
    pixels = list(gray.getdata())
    brightness = (sum(int(v) for v in pixels) / max(1, len(pixels))) / 255.0
    brightness_score = max(0.0, 1.0 - min(1.0, abs(brightness - 0.52) * 1.7))
    sharpness_score = _estimate_sharpness(gray)

    quality_score = (
        (resolution_score * 0.44)
        + (aspect_score * 0.2)
        + (sharpness_score * 0.26)
        + (brightness_score * 0.1)
    )
    return {
        "quality_score": float(max(0.0, min(1.0, quality_score))),
        "width": int(width),
        "height": int(height),
    }


def _estimate_sharpness(image_luma: Any) -> float:
    if Image is None:
        return 0.0
    width, height = image_luma.size
    if width < 16 or height < 16:
        return 0.0
    pixels = list(image_luma.getdata())
    total = 0
    count = 0
    for y in range(height - 1):
        row = y * width
        next_row = (y + 1) * width
        for x in range(width - 1):
            idx = row + x
            dx = abs(int(pixels[idx]) - int(pixels[idx + 1]))
            dy = abs(int(pixels[idx]) - int(pixels[next_row + x]))
            total += dx + dy
            count += 2
    if count <= 0:
        return 0.0
    normalized = (total / count) / 255.0
    return float(max(0.0, min(1.0, normalized * 2.4)))


def _build_dhash(image_bytes: bytes) -> str:
    if not image_bytes or Image is None:
        return ""
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L").resize((9, 8))
    except Exception:
        return ""
    bits: list[str] = []
    pixels = list(image.getdata())
    for row in range(8):
        offset = row * 9
        for col in range(8):
            left = int(pixels[offset + col])
            right = int(pixels[offset + col + 1])
            bits.append("1" if left > right else "0")
    return "".join(bits)


def _is_similar_hash(hash_value: str, selected_hashes: list[str], threshold: int = 3) -> bool:
    if not hash_value:
        return False
    for existing in selected_hashes:
        if not existing or len(existing) != len(hash_value):
            continue
        distance = sum(1 for a, b in zip(hash_value, existing) if a != b)
        if distance <= threshold:
            return True
    return False


def _fetch_image_bytes(url: str) -> tuple[bytes, str, str]:
    headers = {
        "User-Agent": random.choice(_UA_POOL),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://www.bing.com/",
    }
    value = str(url or "").strip()
    if not value or not value.lower().startswith(("http://", "https://")):
        return b"", "", "bad_url"

    try:
        response = requests.get(
            value,
            headers=headers,
            timeout=(8, 14),
            allow_redirects=True,
            stream=True,
        )
        status_code = int(response.status_code or 0)
        content_type = str(response.headers.get("Content-Type") or "").lower()
        if status_code >= 400:
            response.close()
            return b"", content_type, "http_error"
        if content_type and not content_type.startswith("image/"):
            response.close()
            return b"", content_type, "non_image"
        image_bytes = response.content or b""
        response.close()
        if not image_bytes:
            return b"", content_type, "empty"
        return image_bytes, content_type, "ok"
    except Exception:
        return b"", "", "request_error"


def _reject_image_by_text_or_watermark(*, image_bytes: bytes, image_url: str) -> tuple[bool, str]:
    lowered_url = str(image_url or "").lower()
    if any(token in lowered_url for token in _TEXT_WATERMARK_URL_HINTS):
        return True, "url_hint"

    ocr_text = _extract_text_with_ocr(image_bytes)
    ocr_chars = len(re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", ocr_text))
    ocr_lower = str(ocr_text or "").lower()
    if ocr_chars >= 6 and re.search(
        r"(https?://|www\.|@[a-z0-9_]{2,}|facebook|instagram|youtube|tiktok|discord|telegram|weibo|xiaohongshu|fb)",
        ocr_lower,
    ):
        return True, "ocr_promotional_overlay"
    if ocr_chars >= 8 and any(
        token in ocr_lower
        for token in (
            "copyright",
            "all rights reserved",
            "watermark",
            "logo",
            "de games",
            "gift code",
            "giftcode",
            "redeem code",
            "tier list",
            "\u4ee3\u5132",
            "\u793c\u5305\u7801",
            "\u79ae\u5305\u78bc",
            "\u5151\u6362\u7801",
            "\u514c\u63db\u78bc",
            "\u653b\u7565",
            "\u7c89\u7d72\u5718",
            "\u7c89\u4e1d\u56e2",
            "\u95dc\u6ce8",
            "\u5173\u6ce8",
            "\u8a02\u95b1",
            "\u8ba2\u9605",
        )
    ):
        return True, "ocr_watermark_keyword"
    if ocr_chars >= 12:
        return True, "ocr_text_density"

    dark_ratio, bright_ratio = _estimate_luma_extremes(image_bytes)
    if bright_ratio >= 0.84 and dark_ratio >= 0.003:
        return True, "high_contrast_text_like"

    heuristic_score = _estimate_text_overlay_score(image_bytes)
    if heuristic_score >= 0.3:
        return True, "heuristic_text_overlay"

    corner_logo_score = _estimate_corner_logo_risk(image_bytes)
    if corner_logo_score >= 0.27:
        return True, "corner_logo_overlay"

    bottom_banner_score = _estimate_bottom_banner_risk(image_bytes)
    if bottom_banner_score >= 0.11:
        return True, "bottom_banner_overlay"

    if heuristic_score >= 0.17 and (corner_logo_score >= 0.15 or bottom_banner_score >= 0.06):
        return True, "overlay_combo"

    return False, "ok"


def _extract_text_with_ocr(image_bytes: bytes) -> str:
    if not image_bytes or Image is None or pytesseract is None:
        return ""
    if not shutil.which("tesseract"):
        return ""
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L")
        image.thumbnail((1400, 1400))
        text = pytesseract.image_to_string(
            image,
            lang="eng+chi_tra+chi_sim",
            config="--psm 6",
        )
        return str(text or "").strip()
    except Exception:
        return ""


def _estimate_luma_extremes(image_bytes: bytes) -> tuple[float, float]:
    if not image_bytes or Image is None:
        return 0.0, 0.0
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L")
    except Exception:
        return 0.0, 0.0
    image.thumbnail((720, 720))
    pixels = list(image.getdata())
    total = max(1, len(pixels))
    dark_ratio = sum(1 for value in pixels if int(value) <= 45) / total
    bright_ratio = sum(1 for value in pixels if int(value) >= 220) / total
    return float(dark_ratio), float(bright_ratio)


def _estimate_text_overlay_score(image_bytes: bytes) -> float:
    if not image_bytes or Image is None:
        return 0.0
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L")
    except Exception:
        return 0.0

    image.thumbnail((720, 720))
    width, height = image.size
    if width < 80 or height < 80:
        return 0.0

    pixels = list(image.getdata())

    def _row_transition_ratio(y: int) -> float:
        start = y * width
        row = pixels[start : start + width]
        transitions = 0
        for idx in range(1, width):
            if abs(int(row[idx]) - int(row[idx - 1])) >= 44:
                transitions += 1
        return transitions / max(1, width - 1)

    row_ratios = [_row_transition_ratio(y) for y in range(height)]
    dense_rows = sum(1 for value in row_ratios if 0.14 <= value <= 0.78)
    dense_ratio = dense_rows / max(1, height)

    corner_boxes = [
        (0, 0, int(width * 0.32), int(height * 0.18)),
        (int(width * 0.68), 0, width, int(height * 0.18)),
        (0, int(height * 0.82), int(width * 0.32), height),
        (int(width * 0.68), int(height * 0.82), width, height),
    ]
    corner_score = 0.0
    for left, top, right, bottom in corner_boxes:
        crop = image.crop((left, top, right, bottom))
        cw, ch = crop.size
        if cw < 20 or ch < 20:
            continue
        cp = list(crop.getdata())
        local_transitions = 0
        for y in range(ch):
            base = y * cw
            row = cp[base : base + cw]
            for idx in range(1, cw):
                if abs(int(row[idx]) - int(row[idx - 1])) >= 50:
                    local_transitions += 1
        ratio = local_transitions / max(1, (cw - 1) * ch)
        corner_score = max(corner_score, ratio)

    return float((dense_ratio * 0.68) + (corner_score * 1.45))


def _estimate_corner_logo_risk(image_bytes: bytes) -> float:
    if not image_bytes or Image is None:
        return 0.0
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return 0.0

    image.thumbnail((560, 560))
    width, height = image.size
    if width < 120 or height < 120:
        return 0.0

    corner_boxes = [
        (0, 0, int(width * 0.32), int(height * 0.24)),
        (int(width * 0.68), 0, width, int(height * 0.24)),
        (0, int(height * 0.76), int(width * 0.32), height),
        (int(width * 0.68), int(height * 0.76), width, height),
    ]

    best_score = 0.0
    for left, top, right, bottom in corner_boxes:
        crop = image.crop((left, top, right, bottom))
        cw, ch = crop.size
        if cw < 24 or ch < 24:
            continue
        l1 = int(cw * 0.24)
        t1 = int(ch * 0.24)
        r1 = int(cw * 0.76)
        b1 = int(ch * 0.76)
        if r1 - l1 < 8 or b1 - t1 < 8:
            continue

        center_crop = crop.crop((l1, t1, r1, b1))
        center_pixels = list(center_crop.getdata())
        border_pixels: list[tuple[int, int, int]] = []
        full_pixels = list(crop.getdata())
        idx = 0
        for y in range(ch):
            for x in range(cw):
                value = full_pixels[idx]
                idx += 1
                if l1 <= x < r1 and t1 <= y < b1:
                    continue
                border_pixels.append(value)

        if not center_pixels or not border_pixels:
            continue

        center_sat_ratio = _saturation_ratio(center_pixels)
        border_sat_ratio = _saturation_ratio(border_pixels)
        sat_contrast = max(0.0, center_sat_ratio - border_sat_ratio)

        center_mean, center_std = _luma_stats(center_pixels)
        border_mean, border_std = _luma_stats(border_pixels)
        mean_gap = abs(center_mean - border_mean) / 255.0
        std_gap = abs(center_std - border_std) / 128.0

        center_rgb = _rgb_mean(center_pixels)
        border_rgb = _rgb_mean(border_pixels)
        color_gap = _rgb_distance(center_rgb, border_rgb) / 255.0
        color_gap = min(1.0, color_gap / 1.2)

        dominant_ratio = _dominant_color_ratio(full_pixels)
        edge_ratio = _estimate_patch_edge_density(crop.convert("L"), threshold=52)
        edge_penalty = max(0.0, edge_ratio - 0.14)

        score = (
            (color_gap * 0.46)
            + (sat_contrast * 0.28)
            + (mean_gap * 0.17)
            + (std_gap * 0.12)
            + (dominant_ratio * 0.1)
            - (edge_penalty * 0.22)
        )
        best_score = max(best_score, score)

    return float(max(0.0, min(1.0, best_score)))


def _estimate_bottom_banner_risk(image_bytes: bytes) -> float:
    if not image_bytes or Image is None:
        return 0.0
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L")
    except Exception:
        return 0.0

    image.thumbnail((760, 760))
    width, height = image.size
    if width < 140 or height < 140:
        return 0.0

    left = int(width * 0.12)
    right = int(width * 0.88)
    top = int(height * 0.58)
    bottom = int(height * 0.96)
    if right - left < 64 or bottom - top < 48:
        return 0.0

    crop = image.crop((left, top, right, bottom))
    cw, ch = crop.size
    pixels = list(crop.getdata())
    rows_mean: list[float] = []
    rows_std: list[float] = []
    for y in range(ch):
        row = pixels[y * cw : (y + 1) * cw]
        mean_value = sum(int(v) for v in row) / max(1, cw)
        variance = sum((int(v) - mean_value) ** 2 for v in row) / max(1, cw)
        rows_mean.append(mean_value)
        rows_std.append(variance ** 0.5)

    flagged = [1 if (m >= 160 and 10 <= s <= 96) else 0 for m, s in zip(rows_mean, rows_std)]
    longest_run = 0
    current_run = 0
    for value in flagged:
        if value:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    run_ratio = longest_run / max(1, ch)

    edge_ratio = _estimate_patch_edge_density(crop, threshold=48)
    if top > 0:
        top_probe = image.crop((left, max(0, top - int(height * 0.08)), right, top))
        tp = list(top_probe.getdata())
        top_mean = (sum(int(v) for v in tp) / max(1, len(tp))) if tp else 0.0
    else:
        top_mean = 0.0
    band_mean = (sum(rows_mean) / max(1, len(rows_mean))) if rows_mean else 0.0
    contrast_score = max(0.0, min(1.0, (band_mean - top_mean) / 120.0))

    bright_ratio = sum(1 for value in pixels if int(value) >= 215) / max(1, len(pixels))
    dark_ratio = sum(1 for value in pixels if int(value) <= 45) / max(1, len(pixels))
    luma_mix = min(
        1.0,
        (max(bright_ratio, dark_ratio) * 1.4) + (min(bright_ratio, dark_ratio) * 4.2),
    )

    # Smooth gradients can look like "long runs" but are not text banners.
    # Gate the structure score by edge density so we keep precision.
    edge_gate = min(1.0, edge_ratio / 0.035)
    structure_score = (run_ratio * 0.54) + (contrast_score * 0.2) + (luma_mix * 0.26) + (edge_ratio * 0.22)
    score = (structure_score * edge_gate) + (edge_ratio * 0.25)
    return float(max(0.0, min(1.0, score)))


def _estimate_patch_edge_density(patch_luma: Any, *, threshold: int = 50) -> float:
    if Image is None:
        return 0.0
    width, height = patch_luma.size
    if width < 12 or height < 12:
        return 0.0
    pixels = list(patch_luma.getdata())
    transitions = 0
    comparisons = 0

    for y in range(height):
        base = y * width
        row = pixels[base : base + width]
        for idx in range(1, width):
            if abs(int(row[idx]) - int(row[idx - 1])) >= threshold:
                transitions += 1
            comparisons += 1
    for y in range(1, height):
        prev_base = (y - 1) * width
        base = y * width
        for idx in range(width):
            if abs(int(pixels[base + idx]) - int(pixels[prev_base + idx])) >= threshold:
                transitions += 1
            comparisons += 1

    if comparisons <= 0:
        return 0.0
    return float(transitions / comparisons)


def _saturation_ratio(pixels_rgb: list[tuple[int, int, int]], threshold: int = 70) -> float:
    if not pixels_rgb:
        return 0.0
    sat_count = 0
    for r, g, b in pixels_rgb:
        mx = max(int(r), int(g), int(b))
        mn = min(int(r), int(g), int(b))
        if (mx - mn) >= threshold and mx >= 76:
            sat_count += 1
    return float(sat_count / max(1, len(pixels_rgb)))


def _luma_stats(pixels_rgb: list[tuple[int, int, int]]) -> tuple[float, float]:
    if not pixels_rgb:
        return 0.0, 0.0
    values = [
        (0.299 * int(r)) + (0.587 * int(g)) + (0.114 * int(b))
        for r, g, b in pixels_rgb
    ]
    count = max(1, len(values))
    mean_value = sum(values) / count
    variance = sum((v - mean_value) ** 2 for v in values) / count
    return float(mean_value), float(variance ** 0.5)


def _rgb_mean(pixels_rgb: list[tuple[int, int, int]]) -> tuple[float, float, float]:
    if not pixels_rgb:
        return 0.0, 0.0, 0.0
    count = max(1, len(pixels_rgb))
    r_sum = sum(int(r) for r, _, _ in pixels_rgb)
    g_sum = sum(int(g) for _, g, _ in pixels_rgb)
    b_sum = sum(int(b) for _, _, b in pixels_rgb)
    return float(r_sum / count), float(g_sum / count), float(b_sum / count)


def _rgb_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dr = float(a[0] - b[0])
    dg = float(a[1] - b[1])
    db = float(a[2] - b[2])
    return float((dr * dr + dg * dg + db * db) ** 0.5)


def _dominant_color_ratio(pixels_rgb: list[tuple[int, int, int]]) -> float:
    if not pixels_rgb:
        return 0.0
    bins: dict[tuple[int, int, int], int] = {}
    for r, g, b in pixels_rgb:
        key = (int(r) // 32, int(g) // 32, int(b) // 32)
        bins[key] = bins.get(key, 0) + 1
    if not bins:
        return 0.0
    return float(max(bins.values()) / max(1, len(pixels_rgb)))


def _plain_text_length(html: str) -> int:
    return len(_strip_tags(html or ""))



def _audit_polished_content(body_html: str) -> dict[str, int | bool]:
    html = str(body_html or "")
    return {
        "text_len": _plain_text_length(html),
        "h1_count": len(re.findall(r"(?is)<h1\b[^>]*>", html)),
        "h2_count": len(re.findall(r"(?is)<h2\b[^>]*>", html)),
        "h3_count": len(re.findall(r"(?is)<h3\b[^>]*>", html)),
        "table_count": len(re.findall(r"(?is)<table\b", html)),
    }

