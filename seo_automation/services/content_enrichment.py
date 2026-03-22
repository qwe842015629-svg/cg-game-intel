import hashlib
import re
from datetime import datetime
from html import escape
from urllib.parse import quote, urlparse

TXT_GAME = "\u904a\u6232"
TXT_GAME_GUIDE = "\u904a\u6232\u653b\u7565"
TXT_IMAGE = "\u5716\u7247"
TXT_SUMMARY = "\u6458\u8981"
TXT_RELATED_GALLERY = "\u76f8\u95dc\u5716\u96c6"
TXT_KEYWORDS = "\u95dc\u9375\u8a5e"
TXT_PUBLISH_DATE = "\u767c\u5e03\u65e5\u671f"
TXT_DEFAULT_TOPIC = "\u5df4\u54c8\u59c6\u7279\u4e3b\u984c\u5e16"
TXT_EMPTY_BODY = "\u66ab\u6642\u6c92\u6709\u53ef\u5c55\u793a\u7684\u6b63\u6587\u5167\u5bb9\uff0c\u5efa\u8b70\u91cd\u65b0\u751f\u6210\u6587\u7ae0\u4ee5\u53d6\u5f97\u5b8c\u6574\u7d50\u69cb\u3002"
TXT_DEFAULT_SUMMARY_FMT = "\u9019\u7bc7\u5167\u5bb9\u570d\u7e5e {game} \u7684\u7248\u672c\u91cd\u9ede\u3001\u73a9\u6cd5\u5efa\u8b70\u8207\u5132\u503c\u5b89\u5168\u9032\u884c\u6574\u7406\u3002"
TXT_RELATED_LINKS_TITLE = "\u76f8\u95dc\u904a\u6232\u8207\u5b98\u65b9\u9023\u7d50"
TXT_RELATED_LINKS_INTRO = "\u60f3\u7e7c\u7e8c\u63a8\u9032\u5ea6\u6642\uff0c\u5efa\u8b70\u5148\u78ba\u8a8d\u904a\u6232\u7248\u672c\u8207\u5e33\u865f\u5340\u670d\uff0c\u8cc7\u8a0a\u6703\u66f4\u9023\u8cab\u3002"
TXT_RELATED_LINK_INTERNAL = "\u672c\u7ad9\u904a\u6232\u8a73\u60c5"
TXT_RELATED_LINK_GOOGLE = "Google Play \u4e0b\u8f09\u9801"
TXT_RELATED_LINK_APPLE = "App Store \u641c\u5c0b\u9801"
TXT_RECHARGE_HINT = "\u9700\u8981\u88dc\u8db3\u8cc7\u6e90\u6642\uff0c\u53ef\u76f4\u63a5\u5728\u672c\u7ad9\u540c\u6b3e\u904a\u6232\u9801\u6bd4\u5c0d\u5132\u503c\u9805\u76ee\u8207\u7d00\u9304\u6d41\u7a0b\uff0c\u64cd\u4f5c\u6703\u66f4\u9806\u3002"
TXT_INTERNAL_LINK_DEFAULT = "\u76f8\u95dc\u904a\u6232\u8a73\u60c5"

_SUMMARY_URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
_SUMMARY_PREFIX_RE = re.compile(r"(?i)^\s*(?:摘要|summary)\s*[:：\-]\s*")
_SUMMARY_TIMESTAMP_RE = re.compile(
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?\b"
)
_SUMMARY_BRACKET_NOISE_RE = re.compile(r"[【\[]\s*(?:情報|情报|info|news|新聞|新闻)\s*[】\]]", re.I)
_SUMMARY_LINK_SECTION_HINT_RE = re.compile(
    r"(?i)(?:seo-related-links|related game|官方連結|官方链接|google\s*play|app\s*store)"
)
_SUMMARY_SOCIAL_HINT_RE = re.compile(r"(?i)\b(?:facebook|fb|discord|twitter|x\.com|youtube)\b")
_SUMMARY_SOCIAL_PHRASE_RE = re.compile(
    r"(?i)(?:facebook|fb)\s*(?:粉專|粉丝专页|粉絲專頁|fan\s*page)?"
)
_SUMMARY_EMPTY_KEYWORD_RE = re.compile(r"(?i)^(?:摘要|summary)$")


def build_media_items(*, image_urls: list[str], game_name: str) -> list[dict[str, str]]:
    """
    Build deduplicated media metadata list with URL normalization.
    """
    normalized_game_name = (game_name or TXT_GAME).strip()
    seen_md5: set[str] = set()
    items: list[dict[str, str]] = []

    for index, raw_url in enumerate(image_urls or [], start=1):
        url = _normalize_media_url(raw_url)
        if not url:
            continue

        digest = hashlib.md5(url.encode("utf-8")).hexdigest()
        if digest in seen_md5:
            continue
        seen_md5.add(digest)
        items.append(
            {
                "url": url,
                "md5": digest,
                "alt": f"{normalized_game_name} {TXT_IMAGE} {index}",
                "description": f"{normalized_game_name} \u76f8\u95dc{TXT_IMAGE}\u7d20\u6750 {index}",
            }
        )
    return items


def build_media_gallery_html(media_items: list[dict[str, str]]) -> str:
    if not media_items:
        return ""

    blocks: list[str] = []
    for item in media_items:
        url = escape(item.get("url", ""), quote=True)
        alt = escape(item.get("alt", f"{TXT_GAME}{TXT_IMAGE}"))
        blocks.append(
            (
                '<figure class="seo-media-item">'
                f'<img src="{url}" alt="{alt}" loading="lazy" />'
                "</figure>"
            )
        )
    return '<div class="seo-media-gallery">' + "".join(blocks) + "</div>"


def compose_rich_seo_article_html(
    *,
    title: str,
    body_html: str,
    game_name: str,
    summary: str = "",
    keywords: list[str] | None = None,
    search_intent: str = "",
    source_title: str = "",
    source_url: str = "",
    media_gallery_html: str = "",
    media_items: list[dict[str, str]] | None = None,
    generated_at: datetime | None = None,
) -> str:
    """
    Build a stable SEO article layout:
    summary + body + inline images + metadata footer.
    """
    safe_title_text = (title or game_name or TXT_GAME_GUIDE).strip()
    safe_game_name = (game_name or TXT_GAME).strip()

    cleaned_body = _strip_html_document_wrappers(body_html or "")
    cleaned_body = _strip_unsafe_images(cleaned_body)
    cleaned_body = _remove_first_h1(cleaned_body)
    cleaned_body = _strip_existing_seo_structures(cleaned_body)
    if not cleaned_body.strip():
        cleaned_body = f"<p>{TXT_EMPTY_BODY}</p>"

    first_paragraph = _first_paragraph_text(cleaned_body)
    summary_candidate = sanitize_seo_summary_text(summary or "", game_name=safe_game_name, limit=280)
    if not summary_candidate or _is_summary_too_similar(summary_candidate, first_paragraph):
        summary_candidate = sanitize_seo_summary_text(
            _build_article_summary(cleaned_body, safe_game_name),
            game_name=safe_game_name,
            limit=280,
        )
    summary_text = _truncate_text(summary_candidate, 280)
    if not summary_text:
        summary_text = TXT_DEFAULT_SUMMARY_FMT.format(game=safe_game_name)

    merged_keywords = merge_unique_tags(
        base_tags=keywords or [],
        extra_tags=[safe_game_name],
        limit=12,
    )
    keyword_text = "\u3001".join(merged_keywords[:10]) if merged_keywords else safe_game_name

    publish_dt = generated_at or datetime.now()
    publish_text = publish_dt.strftime("%Y-%m-%d")

    inline_media_items = media_items or []
    inline_body_html, inline_inserted = _inject_media_after_h2(cleaned_body, inline_media_items)

    gallery_section = ""
    if inline_media_items and not inline_inserted:
        fallback_gallery = media_gallery_html or build_media_gallery_html(inline_media_items)
        if fallback_gallery:
            gallery_section = (
                '<section class="seo-media-block">'
                f"<h2>{TXT_RELATED_GALLERY}</h2>"
                f"{fallback_gallery}"
                "</section>"
            )
    elif media_gallery_html and not inline_media_items:
        gallery_section = (
            '<section class="seo-media-block">'
            f"<h2>{TXT_RELATED_GALLERY}</h2>"
            f"{media_gallery_html}"
            "</section>"
        )

    return (
        '<article class="seo-article-shell">'
        '<header class="seo-article-header">'
        f"<h1>{escape(safe_title_text[:220])}</h1>"
        "</header>"
        f'<div class="seo-summary"><strong>{TXT_SUMMARY}</strong>\uff1a{escape(summary_text)}</div>'
        f'<section class="seo-main-content">{inline_body_html}</section>'
        f"{gallery_section}"
        '<footer class="seo-metadata">'
        f"<p><strong>{TXT_KEYWORDS}</strong>\uff1a{escape(keyword_text)}</p>"
        f"<p><strong>{TXT_PUBLISH_DATE}</strong>\uff1a{escape(publish_text)}</p>"
        "</footer>"
        "</article>"
    )


def build_standalone_seo_html_document(
    *,
    title: str,
    meta_description: str,
    meta_keywords: str,
    body_html: str,
) -> str:
    safe_title = escape((title or "SEO\u6587\u7ae0").strip()[:220])
    safe_description = escape((meta_description or "").strip()[:300], quote=True)
    safe_keywords = escape((meta_keywords or "").strip()[:400], quote=True)

    return (
        "<!DOCTYPE html>"
        '<html lang="zh-Hant">'
        "<head>"
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<meta name="description" content="{safe_description}">'
        f'<meta name="keywords" content="{safe_keywords}">'
        '<meta name="author" content="SEO\u6587\u7ae0\u751f\u6210\u5668">'
        f"<title>{safe_title}</title>"
        "<style>"
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang TC','Microsoft JhengHei',sans-serif;line-height:1.85;max-width:980px;margin:42px auto;padding:0 20px;color:#24364c;background:#f4f7fb;}"
        "article{background:#fff;border:1px solid #e0e8f4;border-radius:16px;padding:30px 28px;box-shadow:0 14px 28px rgba(18,46,93,.08);}"
        "h1{color:#1f3656;border-bottom:3px solid #2f80ed;padding-bottom:12px;margin:0 0 18px;font-size:2rem;line-height:1.35;}"
        "h2{color:#2a4a71;margin:40px 0 14px;font-size:1.45rem;line-height:1.4;}"
        "h3{color:#2f5d8f;margin:28px 0 12px;font-size:1.16rem;line-height:1.45;}"
        "p{margin:0 0 16px;color:#2f4058;letter-spacing:.01em;}"
        ".seo-main-content{margin-top:10px;}"
        ".seo-main-content > *:last-child{margin-bottom:0;}"
        "img{display:block;max-width:100%;height:auto;border-radius:12px;margin:18px auto 20px;box-shadow:0 4px 14px rgba(0,0,0,.14);background:#edf3fb;}"
        ".seo-inline-media{margin:16px 0 22px;}"
        ".seo-summary{background:#eef6ff;padding:16px 18px;border-left:4px solid #2f80ed;border-radius:10px;margin:16px 0 26px;line-height:1.8;}"
        "ul,ol{list-style:none;margin:10px 0 20px;padding-left:0;}"
        "li{position:relative;margin:9px 0;padding-left:1.5em;}"
        "li::before{content:'✨';position:absolute;left:0;top:0;}"
        ".seo-related-links{margin-top:30px;padding:18px;border:1px solid #d6e5fb;border-radius:12px;background:linear-gradient(180deg,#f8fcff,#eef5ff);}"
        ".seo-related-links h2{margin-top:0;}"
        ".seo-related-links p{margin-bottom:12px;}"
        ".seo-related-links ul{margin:8px 0 4px;}"
        ".seo-related-links li{margin:8px 0;padding-left:0;}"
        ".seo-related-links li::before{content:'';position:static;}"
        ".seo-related-links a{color:#1c5fa7;text-decoration:none;border-bottom:1px dashed #8eb7ea;}"
        ".seo-related-links a:hover{color:#123f6f;border-bottom-color:#123f6f;}"
        ".seo-recharge-note{margin-top:10px;color:#3a5678;}"
        "table{width:100%;border-collapse:collapse;margin:20px 0 22px;border:1px solid #d8e3f1;border-radius:10px;overflow:hidden;}"
        "th,td{border:1px solid #d8e3f1;padding:10px 12px;text-align:left;vertical-align:top;}"
        "th{background:#f2f6fc;color:#35557b;}"
        ".seo-metadata{background:#edf3fa;padding:14px 16px;border-radius:10px;margin-top:30px;font-size:.94em;line-height:1.8;}"
        "</style>"
        "</head>"
        "<body>"
        f"{body_html}"
        "</body>"
        "</html>"
    )


def inject_game_internal_link(
    *,
    body_html: str,
    game_id: int | None,
    game_title: str = "",
    google_play_id: str = "",
    app_store_url: str = "",
) -> str:
    cleaned_html = _strip_existing_related_links_blocks(body_html or "")

    normalized_game_title = (game_title or "").strip()
    if game_id:
        target = f"/games/{game_id}"
    elif normalized_game_title:
        target = f"/games?keyword={quote(normalized_game_title, safe='')}"
    else:
        target = "/games"

    label = escape(normalized_game_title or TXT_INTERNAL_LINK_DEFAULT)
    safe_target = escape(target, quote=True)
    package_id = str(google_play_id or "").strip()
    if package_id:
        google_href = f"https://play.google.com/store/apps/details?id={quote(package_id, safe='')}"
    else:
        query = quote(normalized_game_title or TXT_GAME, safe="")
        google_href = f"https://play.google.com/store/search?q={query}&c=apps"
    query = quote(normalized_game_title or TXT_GAME, safe="")
    apple_href = f"https://apps.apple.com/tw/iphone/search?term={query}"

    links_html = (
        '<section class="seo-related-links">'
        f"<h2>{TXT_RELATED_LINKS_TITLE}</h2>"
        f"<p>{TXT_RELATED_LINKS_INTRO}</p>"
        "<ul>"
        f'<li>🧭 <a href="{safe_target}" target="_blank" rel="noopener">{TXT_RELATED_LINK_INTERNAL}：{label}</a></li>'
        f'<li>🎮 <a href="{escape(google_href, quote=True)}" target="_blank" rel="noopener noreferrer">{TXT_RELATED_LINK_GOOGLE}：{label}</a></li>'
        f'<li>🍎 <a href="{escape(apple_href, quote=True)}" target="_blank" rel="noopener noreferrer">{TXT_RELATED_LINK_APPLE}：{label}</a></li>'
        "</ul>"
        f'<p class="seo-recharge-note">{TXT_RECHARGE_HINT}</p>'
        "</section>"
    )
    return cleaned_html + links_html


def _strip_existing_related_links_blocks(html: str) -> str:
    value = str(html or "")
    if not value.strip():
        return ""

    # Remove previously injected standardized block(s).
    value = re.sub(
        r"(?is)<section\b[^>]*class=['\"][^'\"]*seo-related-links[^'\"]*['\"][^>]*>.*?</section>",
        " ",
        value,
    )

    # Remove legacy loose block without `.seo-related-links` wrapper.
    heading_pattern = r"(?:相關遊戲與官方連結|相关游戏与官方链接)"
    loose_block_pattern = (
        rf"(?is)<h[23]\b[^>]*>\s*{heading_pattern}\s*</h[23]>"
        r"(?:\s*<p\b[^>]*>.*?</p>)?"
        r"(?:\s*<ul\b[^>]*>.*?</ul>)?"
        r"(?:\s*<p\b[^>]*>.*?</p>)?"
    )
    value = re.sub(loose_block_pattern, " ", value)

    value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
    return value.strip()


def build_meta_fields(*, title: str, body_html: str, default_title: str = "") -> dict[str, str]:
    meta_title = (title or default_title or TXT_GAME_GUIDE).strip()[:60]
    summary_block_match = re.search(
        r"(?is)<(?:div|section)\b[^>]*class=['\"][^'\"]*seo-summary[^'\"]*['\"][^>]*>(.*?)</(?:div|section)>",
        body_html or "",
    )
    summary_block_text = _clean_plain_text(summary_block_match.group(1) if summary_block_match else "")
    text_content = _clean_plain_text(body_html or "")

    meta_description = sanitize_seo_summary_text(summary_block_text, limit=160)
    if not meta_description:
        meta_description = sanitize_seo_summary_text(text_content, limit=160)
    if not meta_description:
        relaxed = _SUMMARY_URL_RE.sub(" ", text_content)
        relaxed = re.sub(r"\s+", " ", relaxed).strip()
        meta_description = _truncate_text(relaxed, 160)
    if not meta_description:
        meta_description = meta_title[:160]

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
    }


def merge_unique_tags(*, base_tags: list[str], extra_tags: list[str] | None = None, limit: int = 12) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for raw in [*(base_tags or []), *(extra_tags or [])]:
        tag = (raw or "").strip()
        if not tag:
            continue
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(tag)
        if len(merged) >= limit:
            break
    return merged


def _build_inline_media_html(item: dict[str, str]) -> str:
    url = escape(str(item.get("url") or "").strip(), quote=True)
    if not url:
        return ""
    alt = escape(str(item.get("alt") or f"{TXT_GAME}{TXT_IMAGE}").strip())
    return (
        '<figure class="seo-inline-media">'
        f'<img src="{url}" alt="{alt}" loading="lazy" />'
        "</figure>"
    )


def _inject_media_after_h2(body_html: str, media_items: list[dict[str, str]]) -> tuple[str, bool]:
    if not media_items:
        return body_html, False

    inline_blocks = [block for block in (_build_inline_media_html(item) for item in media_items) if block]
    if not inline_blocks:
        return body_html, False

    index_box = {"idx": 0}
    inserted_box = {"count": 0}

    def _replace_h2(match: re.Match) -> str:
        idx = index_box["idx"]
        if idx >= len(inline_blocks):
            return match.group(0)
        block = inline_blocks[idx]
        index_box["idx"] = idx + 1
        inserted_box["count"] += 1
        return match.group(0) + block

    replaced_body, hit_count = re.subn(
        r"(?is)<h2\b[^>]*>.*?</h2>",
        _replace_h2,
        body_html or "",
    )
    if hit_count > 0 and inserted_box["count"] > 0:
        return replaced_body, True

    first_block = inline_blocks[0]
    paragraph_hit = re.search(r"(?is)</p>", body_html or "")
    if paragraph_hit:
        injected = re.sub(r"(?is)</p>", lambda m: m.group(0) + first_block, body_html, count=1)
        return injected, True

    return first_block + (body_html or ""), True


def _strip_html_document_wrappers(html: str) -> str:
    value = str(html or "")
    value = re.sub(r"(?is)<!doctype[^>]*>", " ", value)
    value = re.sub(r"(?is)<html[^>]*>|</html>", " ", value)
    value = re.sub(r"(?is)<head[^>]*>.*?</head>", " ", value)
    value = re.sub(r"(?is)<body[^>]*>|</body>", " ", value)
    value = re.sub(r"(?is)<meta[^>]*>", " ", value)
    value = re.sub(r"(?is)<title[^>]*>.*?</title>", " ", value)
    value = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", value)
    value = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", value)
    value = re.sub(r"\s+\n", "\n", value)
    return value.strip()


def _remove_first_h1(html: str) -> str:
    return re.sub(r"(?is)<h1[^>]*>.*?</h1>", " ", html or "", count=1).strip()


def _strip_existing_seo_structures(html: str) -> str:
    value = str(html or "")
    if not value.strip():
        return ""

    # Remove previous shell wrappers to avoid nesting.
    value = re.sub(
        r"(?is)<article\b[^>]*class=['\"][^'\"]*seo-article-shell[^'\"]*['\"][^>]*>",
        " ",
        value,
    )
    value = re.sub(r"(?is)</article>", " ", value)

    # Keep only one summary and one metadata area by removing legacy/duplicated blocks.
    value = re.sub(
        r"(?is)<(?:div|section)\b[^>]*class=['\"][^'\"]*seo-summary[^'\"]*['\"][^>]*>.*?</(?:div|section)>",
        " ",
        value,
    )
    value = re.sub(
        r"(?is)<(?:footer|div|section)\b[^>]*class=['\"][^'\"]*seo-metadata[^'\"]*['\"][^>]*>.*?</(?:footer|div|section)>",
        " ",
        value,
    )

    # Remove plain-text summary paragraphs generated by upstream prompt.
    value = re.sub(
        r"(?is)<(?:p|div|section)\b[^>]*>\s*(?:<strong>\s*)?(?:摘要|摘要[:：])\s*(?:</strong>)?.*?</(?:p|div|section)>",
        " ",
        value,
    )

    # Remove legacy keyword/date rows from body; compose_rich_seo_article_html will append one canonical footer.
    value = re.sub(
        r"(?is)<p\b[^>]*>\s*<strong>\s*(?:關鍵詞|关键词)\s*</strong>\s*[:：]?.*?</p>",
        " ",
        value,
    )
    value = re.sub(
        r"(?is)<p\b[^>]*>\s*<strong>\s*(?:發佈日期|發布日期|发布日期)\s*</strong>\s*[:：]?.*?</p>",
        " ",
        value,
    )
    value = re.sub(
        r"(?is)<(?:div|section)\b[^>]*>\s*(?:<p\b[^>]*>\s*<strong>\s*(?:關鍵詞|关键词)\s*</strong>.*?</p>\s*)+(?:<p\b[^>]*>\s*<strong>\s*(?:發佈日期|發布日期|发布日期)\s*</strong>.*?</p>\s*)+</(?:div|section)>",
        " ",
        value,
    )

    value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
    return value.strip()


def _first_paragraph_text(html: str) -> str:
    if not html:
        return ""
    match = re.search(r"(?is)<p[^>]*>(.*?)</p>", html)
    if match:
        return _clean_plain_text(match.group(1))
    return _clean_plain_text(html)


def _normalize_summary_chunk(value: str) -> str:
    text = _clean_plain_text(value)
    if not text:
        return ""
    text = _SUMMARY_URL_RE.sub(" ", text)
    text = _SUMMARY_BRACKET_NOISE_RE.sub(" ", text)
    text = _SUMMARY_TIMESTAMP_RE.sub(" ", text)
    text = _SUMMARY_SOCIAL_PHRASE_RE.sub(" ", text)
    text = _SUMMARY_PREFIX_RE.sub("", text)
    text = re.sub(r"(?i)\b(?:摘要|summary)\s*[:：]\s*", " ", text)
    text = re.sub(r"[|｜]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.;:!?，。；：！？-")
    if _SUMMARY_EMPTY_KEYWORD_RE.fullmatch(text or ""):
        return ""
    return text


def _looks_like_summary_noise(value: str) -> bool:
    text = _normalize_summary_chunk(value)
    if not text:
        return True
    if _SUMMARY_LINK_SECTION_HINT_RE.search(text):
        return True
    if _SUMMARY_SOCIAL_HINT_RE.search(text) and _SUMMARY_URL_RE.search(str(value or "")):
        return True
    if re.search(r"(?i)\b(?:http|www)\b", text):
        return True
    if len(re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", text)) < 8:
        return True
    return False


def sanitize_seo_summary_text(summary: str, *, game_name: str = "", limit: int = 280) -> str:
    text = _clean_plain_text(summary)
    if not text:
        return ""

    chunks = re.split(r"(?<=[。！？!?；;])|[\n\r]+|(?<=\.)\s+", text)
    seen: set[str] = set()
    cleaned_chunks: list[str] = []

    for chunk in chunks:
        normalized_chunk = _normalize_summary_chunk(chunk)
        if not normalized_chunk:
            continue
        if _looks_like_summary_noise(normalized_chunk):
            continue
        dedupe_key = re.sub(r"[\s\W_]+", "", normalized_chunk.lower())
        if not dedupe_key or dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        cleaned_chunks.append(normalized_chunk)

    if not cleaned_chunks:
        fallback_text = _normalize_summary_chunk(text)
        if fallback_text and not _looks_like_summary_noise(fallback_text):
            cleaned_chunks = [fallback_text]

    summary_text = _clean_plain_text(" ".join(cleaned_chunks[:3]))
    if not summary_text:
        return ""
    if game_name and len(summary_text) < 14:
        summary_text = f"{game_name} 重點整理：{summary_text}"
    return _truncate_text(summary_text, max(16, int(limit)))


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[。！？!?])|[\n\r]+", str(text or ""))
    results: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        line = _normalize_summary_chunk(chunk)
        if len(line) < 8:
            continue
        if _looks_like_summary_noise(line):
            continue
        key = re.sub(r"\s+", "", line)
        if key in seen:
            continue
        seen.add(key)
        results.append(line)
    return results


def _is_summary_too_similar(summary_text: str, first_paragraph: str) -> bool:
    left = _clean_plain_text(summary_text)
    right = _clean_plain_text(first_paragraph)
    if not left or not right:
        return False

    left_norm = re.sub(r"[^\w\u4e00-\u9fff]", "", left.lower())
    right_norm = re.sub(r"[^\w\u4e00-\u9fff]", "", right.lower())
    if not left_norm or not right_norm:
        return False

    if left_norm in right_norm or right_norm in left_norm:
        return True

    left_tokens = set(re.findall(r"[a-z0-9\u4e00-\u9fff]{2,20}", left_norm))
    right_tokens = set(re.findall(r"[a-z0-9\u4e00-\u9fff]{2,20}", right_norm))
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    ratio = overlap / max(1, min(len(left_tokens), len(right_tokens)))
    return ratio >= 0.86


def _build_article_summary(body_html: str, game_name: str) -> str:
    html = str(body_html or "")
    headings_raw = re.findall(r"(?is)<h[23]\b[^>]*>(.*?)</h[23]>", html)
    headings: list[str] = []
    for raw in headings_raw:
        heading = _clean_plain_text(raw)
        if not heading or heading in headings:
            continue
        headings.append(heading)
        if len(headings) >= 3:
            break

    plain = _clean_plain_text(html)
    sentences = _split_sentences(plain)
    first_paragraph = _first_paragraph_text(html)

    lead_sentence = ""
    for sentence in sentences:
        if not _is_summary_too_similar(sentence, first_paragraph):
            lead_sentence = sentence
            break
    if not lead_sentence and sentences:
        lead_sentence = sentences[0]

    focus_sentence = ""
    focus_keywords = ("重點", "建議", "流程", "注意", "資源", "裝備", "陣容", "儲值", "安全", "玩法")
    for sentence in sentences:
        if sentence == lead_sentence:
            continue
        if any(keyword in sentence for keyword in focus_keywords):
            focus_sentence = sentence
            break
    if not focus_sentence:
        for sentence in sentences:
            if sentence != lead_sentence:
                focus_sentence = sentence
                break

    parts: list[str] = []
    if headings:
        parts.append(f"本文整理{game_name}的{'、'.join(headings[:3])}，")
    if lead_sentence:
        parts.append(lead_sentence)
    if focus_sentence:
        parts.append(focus_sentence)

    summary = sanitize_seo_summary_text("".join(parts), game_name=game_name, limit=280)
    return summary or TXT_DEFAULT_SUMMARY_FMT.format(game=game_name)


def _truncate_text(value: str, limit: int) -> str:
    raw = _clean_plain_text(value)
    if len(raw) <= limit:
        return raw
    return raw[: max(limit - 3, 0)].rstrip() + "..."


def _clean_plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def _strip_unsafe_images(html: str) -> str:
    """
    Remove local disk-path images from model output (e.g. E:\\xx\\a.webp).
    Keep only web-safe src values.
    """

    def _replace(match: re.Match) -> str:
        tag = match.group(0)
        src_match = re.search(r"""src\s*=\s*['\"]([^'\"]+)['\"]""", tag, flags=re.I)
        if not src_match:
            return ""
        src = _normalize_media_url(src_match.group(1) or "")
        if not src:
            return ""
        return re.sub(r"""src\s*=\s*['\"][^'\"]+['\"]""", f'src="{escape(src, quote=True)}"', tag, flags=re.I)

    return re.sub(r"(?is)<img\b[^>]*>", _replace, html or "")


def _normalize_media_url(raw_url: str) -> str:
    value = str(raw_url or "").strip()
    if not value:
        return ""

    if value.startswith("//"):
        return f"https:{value}"

    lowered = value.lower()
    if lowered.startswith(("http://", "https://", "/media/", "/static/", "data:image/")):
        return value

    normalized = value.replace("\\", "/")

    if re.match(r"^[a-zA-Z]:/", normalized):
        media_index = normalized.lower().find("/media/")
        if media_index != -1:
            return normalized[media_index:]
        return ""

    media_match = re.search(r"/media/[\w\-./%]+", normalized, flags=re.I)
    if media_match:
        return media_match.group(0)

    if normalized.startswith("media/"):
        return f"/{normalized}"

    if normalized.startswith("./media/"):
        return normalized[1:]

    return ""


def _is_forum_source_url(url: str) -> bool:
    value = str(url or "").strip()
    if not value:
        return False
    try:
        host = urlparse(value).netloc.lower()
    except Exception:
        return False
    return "forum.gamer.com.tw" in host
