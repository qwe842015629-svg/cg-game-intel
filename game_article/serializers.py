import re
from urllib.parse import quote
from html import escape

from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers

from game_recharge.i18n_utils import localize_text, resolve_request_locale
from game_page.models import GamePage
from .models import Article, ArticleCategory, ArticleTag, Comment

try:
    from seo_automation.services.content_enrichment import sanitize_seo_summary_text
except Exception:  # pragma: no cover
    def sanitize_seo_summary_text(raw: str, game_name: str = "", limit: int = 160) -> str:
        text = re.sub(r"(?i)\b(?:https?://|www\.)\S+", " ", str(raw or ""))
        text = re.sub(r"\s+", " ", text).strip()
        return text[: max(1, int(limit or 160))]


def _extract_first_image_src(html: str) -> str:
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', str(html or ""), flags=re.I)
    return str(match.group(1) if match else "").strip()


def _normalize_image_url(raw: str, request=None) -> str:
    value = str(raw or "").strip()
    if not value:
        return ""
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("/") and request:
        try:
            return request.build_absolute_uri(value)
        except Exception:
            return value
    return value


def _resolve_article_image_url(instance: Article, request=None) -> str:
    # 1) Cover image uploaded for article.
    if getattr(instance, "cover_image", None):
        try:
            cover_url = _normalize_image_url(instance.cover_image.url, request=request)
            if cover_url:
                return cover_url
        except Exception:
            pass

    # 2) First inline image from article HTML.
    content_src = _extract_first_image_src(getattr(instance, "content", ""))
    normalized_content_src = _normalize_image_url(content_src, request=request)
    if normalized_content_src:
        return normalized_content_src

    # 3) Related game local icon.
    game = getattr(instance, "game", None)
    if game and getattr(game, "icon_image", None):
        try:
            icon_url = _normalize_image_url(game.icon_image.url, request=request)
            if icon_url:
                return icon_url
        except Exception:
            pass

    # 4) Related game external icon.
    if game:
        icon_external = _normalize_image_url(getattr(game, "icon_external_url", ""), request=request)
        if icon_external:
            return icon_external

    return ""


def _resolve_serializer_locale(context: dict) -> str:
    request = context.get("request") if isinstance(context, dict) else None
    return resolve_request_locale(request)


def _localize_article_field(default_text, i18n_map, locale: str) -> str:
    """
    Keep zh-CN as source-of-truth from the main field so frontend matches admin editor content.
    Other locales still use i18n map with fallback.
    """
    normalized = str(locale or "").strip().lower()
    if normalized.startswith("zh") and not any(tag in normalized for tag in ("tw", "hk", "hant")):
        preferred = str(default_text or "").strip()
        if preferred:
            return preferred
    return localize_text(default_text, i18n_map, locale)


def _localized_category_name(category: ArticleCategory | None, locale: str) -> str:
    if not category:
        return "游戏资讯"
    return localize_text(getattr(category, "name", ""), getattr(category, "name_i18n", {}), locale) or "游戏资讯"


def _localized_tag_name(tag: ArticleTag, locale: str) -> str:
    return localize_text(getattr(tag, "name", ""), getattr(tag, "name_i18n", {}), locale)


def _normalize_game_keyword(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return ""
    text = re.sub(r"[|｜:：\-—_].*$", "", text).strip()
    text = re.sub(r"(攻略|教學|教程|心得|懶人包|新手|版本|玩法|儲值|充值|代儲).*$", "", text).strip()
    return text


_SUMMARY_BLOCK_RE = re.compile(
    r'(?is)<(?:div|section)\b[^>]*class=["\'][^"\']*seo-summary[^"\']*["\'][^>]*>.*?</(?:div|section)>'
)

_RELATED_LINKS_BLOCK_RE = re.compile(
    r'(?is)<section\b[^>]*class=["\'][^"\']*seo-related-links[^"\']*["\'][^>]*>.*?</section>'
)
_RELATED_LINKS_LEGACY_HEADING_RE = re.compile(
    r"(?is)<h[23]\b[^>]*>\s*(?:相關遊戲與官方連結|相关游戏与官方链接|Related Game and Official Links)\s*</h[23]>\s*"
    r"(?:<p\b[^>]*>.*?</p>\s*)?"
    r"(?:<ul\b[^>]*>.*?</ul>\s*)?"
    r"(?:<p\b[^>]*>.*?</p>\s*)?"
)


def _normalize_locale_for_related_links(locale: str) -> str:
    value = str(locale or "").strip().lower()
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
    return "en"


def _related_links_copy(locale: str) -> dict[str, str]:
    normalized = _normalize_locale_for_related_links(locale)
    if normalized == "zh-TW":
        return {
            "title": "相關遊戲與官方連結",
            "intro": "想繼續推進進度時，建議先確認版本、區服與帳號資訊，流程會更穩定。",
            "internal": "本站遊戲詳情",
            "google": "Google Play 下載頁",
            "apple": "App Store 搜尋頁",
            "note": "需要補足資源時，可直接在本站對應遊戲頁完成操作與查單，流程更順。",
            "summary_label": "摘要",
        }
    if normalized == "zh-CN":
        return {
            "title": "相关游戏与官方链接",
            "intro": "想继续推进进度时，建议先确认版本、区服与账号信息，流程会更稳定。",
            "internal": "本站游戏详情",
            "google": "Google Play 下载页",
            "apple": "App Store 搜索页",
            "note": "需要补资源时，可直接在本站对应游戏页完成操作与查单，流程更顺。",
            "summary_label": "摘要",
        }
    return {
        "title": "Related Game and Official Links",
        "intro": "Before proceeding, confirm version, server, and account details for a smoother process.",
        "internal": "Game detail on this site",
        "google": "Google Play page",
        "apple": "App Store search",
        "note": "Need to top up? Open the game page on this site to complete and verify your order quickly.",
        "summary_label": "Summary",
    }


def _build_localized_site_path(path: str, locale: str) -> str:
    normalized_locale = _normalize_locale_for_related_links(locale)
    raw_path = str(path or "").strip()
    if not raw_path:
        return f"/{normalized_locale}"
    normalized_path = raw_path if raw_path.startswith("/") else f"/{raw_path}"
    return f"/{normalized_locale}{normalized_path}"


def _resolve_app_store_search_url(game_name: str, locale: str) -> str:
    locale_key = _normalize_locale_for_related_links(locale)
    storefront = {
        "zh-CN": "cn",
        "zh-TW": "tw",
        "en": "us",
        "ja": "jp",
        "ko": "kr",
        "fr": "fr",
        "de": "de",
        "vi": "vn",
        "th": "th",
    }.get(locale_key, "us")
    return f"https://apps.apple.com/{storefront}/search?term={quote(game_name, safe='')}"


def _clean_article_summary_text(value: str, *, game_name: str = "", limit: int = 500) -> str:
    cleaned = sanitize_seo_summary_text(value or "", game_name=game_name, limit=min(limit, 280))
    if cleaned:
        return cleaned[:limit]
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"(?i)\b(?:https?://|www\.)\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _resolve_related_game_for_article(instance: Article) -> GamePage | None:
    game = getattr(instance, "game", None)
    if game:
        return game

    keyword = _normalize_game_keyword(getattr(instance, "title", ""))
    if not keyword:
        return None

    exact = (
        GamePage.objects.filter(
            models.Q(title__iexact=keyword) | models.Q(title_tw__iexact=keyword)
        )
        .order_by("-is_hot", "-is_recommended", "-updated_at")
        .first()
    )
    if exact:
        return exact

    if len(keyword) < 2:
        return None

    return (
        GamePage.objects.filter(
            models.Q(title__icontains=keyword) | models.Q(title_tw__icontains=keyword)
        )
        .order_by("-is_hot", "-is_recommended", "-updated_at")
        .first()
    )


def _build_related_links_block(instance: Article, locale: str = "zh-CN") -> str:
    related_game = _resolve_related_game_for_article(instance)
    game_name = (
        str(getattr(related_game, "title", "") or "").strip()
        or _normalize_game_keyword(getattr(instance, "title", ""))
        or "游戏"
    )
    copy = _related_links_copy(locale)

    if related_game:
        internal_href = _build_localized_site_path(f"/games/{related_game.id}", locale)
    else:
        internal_href = _build_localized_site_path(f"/games?keyword={quote(game_name, safe='')}", locale)

    if related_game and str(getattr(related_game, "google_play_id", "") or "").strip():
        google_href = (
            "https://play.google.com/store/apps/details"
            f"?id={quote(str(related_game.google_play_id).strip(), safe='')}"
        )
    else:
        google_href = f"https://play.google.com/store/search?q={quote(game_name, safe='')}&c=apps"

    apple_href = _resolve_app_store_search_url(game_name, locale=locale)

    return (
        '<section class="seo-related-links">'
        f"<h2>{copy['title']}</h2>"
        f"<p>{copy['intro']}</p>"
        "<ul>"
        f'<li>🧭 <a href="{internal_href}" target="_blank" rel="noopener">{copy["internal"]}：{game_name}</a></li>'
        f'<li>🎮 <a href="{google_href}" target="_blank" rel="noopener noreferrer">{copy["google"]}：{game_name}</a></li>'
        f'<li>🍎 <a href="{apple_href}" target="_blank" rel="noopener noreferrer">{copy["apple"]}：{game_name}</a></li>'
        "</ul>"
        f'<p class="seo-recharge-note">{copy["note"]}</p>'
        "</section>"
    )


def _strip_existing_related_links_blocks(content: str) -> str:
    body = str(content or "")
    if not body.strip():
        return ""
    body = _RELATED_LINKS_BLOCK_RE.sub(" ", body)
    body = _RELATED_LINKS_LEGACY_HEADING_RE.sub(" ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def _normalize_existing_summary_block(content: str, *, locale: str, summary_text: str, game_name: str) -> str:
    body = str(content or "")
    summary_exists = bool(_SUMMARY_BLOCK_RE.search(body))
    plain_summary_exists = bool(re.search(r"(?i)\b(?:摘要|summary)\s*[:：]", body))
    if not summary_exists and not plain_summary_exists:
        return body

    cleaned_summary = _clean_article_summary_text(summary_text, game_name=game_name, limit=280)
    if not cleaned_summary:
        return body

    label = _related_links_copy(locale).get("summary_label", "Summary")
    canonical_block = f'<div class="seo-summary"><strong>{escape(label)}</strong>：{escape(cleaned_summary)}</div>'

    normalized = _SUMMARY_BLOCK_RE.sub(" ", body)
    normalized = re.sub(
        r"(?is)<(?:p|div|section)\b[^>]*>\s*(?:<strong>\s*)?(?:摘要|summary)\s*(?:[:：]|</strong>\s*[:：]).*?</(?:p|div|section)>",
        " ",
        normalized,
    )
    normalized = re.sub(r"\n\s*\n\s*\n+", "\n\n", normalized).strip()

    if not normalized:
        return canonical_block

    if re.search(r"(?is)</header>", normalized):
        return re.sub(r"(?is)</header>", f"</header>{canonical_block}", normalized, count=1)

    if re.search(r"(?is)<h1\b[^>]*>.*?</h1>", normalized):
        return re.sub(
            r"(?is)<h1\b[^>]*>.*?</h1>",
            lambda match: match.group(0) + canonical_block,
            normalized,
            count=1,
        )

    return canonical_block + normalized


def _ensure_related_links_block(content: str, instance: Article, locale: str = "zh-CN") -> str:
    body = _strip_existing_related_links_blocks(content)
    related_block = _build_related_links_block(instance, locale=locale)
    if not body:
        return related_block
    return body + related_block


def _remove_source_and_related_blocks(content: str) -> str:
    body = str(content or "")
    body = re.sub(
        r'<section[^>]*class=["\'][^"\']*seo-metadata[^"\']*["\'][^>]*>.*?</section>',
        "",
        body,
        flags=re.I | re.S,
    )
    body = _strip_existing_related_links_blocks(body)
    return body


class ArticleCategorySerializer(serializers.ModelSerializer):
    """文章分类序列化器"""

    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = ArticleCategory
        fields = [
            "id",
            "name",
            "description",
            "sort_order",
            "is_active",
            "articles_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_articles_count(self, obj):
        return obj.articles.filter(status="published").count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["name"] = localize_text(instance.name, getattr(instance, "name_i18n", {}), locale)
        data["description"] = localize_text(
            instance.description, getattr(instance, "description_i18n", {}), locale
        )
        return data


class ArticleTagSerializer(serializers.ModelSerializer):
    """文章标签序列化器"""

    class Meta:
        model = ArticleTag
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["name"] = localize_text(instance.name, getattr(instance, "name_i18n", {}), locale)
        return data


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简版序列化器"""

    class Meta:
        model = User
        fields = ["id", "username"]


class ArticleListSerializer(serializers.ModelSerializer):
    """文章列表序列化器"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    game_name = serializers.CharField(source="game.title", read_only=True, allow_null=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "category_name",
            "author_name",
            "cover_image",
            "excerpt",
            "tags",
            "published_at",
            "read_time",
            "view_count",
        ]

    def get_tags(self, obj):
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        return [_localized_tag_name(tag, locale) for tag in obj.tags.all()]

    def _build_image_url(self, instance):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _resolve_article_image_url(instance, request=request)

    def to_representation(self, instance):
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        image_url = self._build_image_url(instance)
        title = _localize_article_field(instance.title, getattr(instance, "title_i18n", {}), locale)
        game_name_for_summary = str(getattr(getattr(instance, "game", None), "title", "") or "").strip()
        if not game_name_for_summary:
            game_name_for_summary = _normalize_game_keyword(title)
        excerpt = _clean_article_summary_text(
            _localize_article_field(instance.excerpt, getattr(instance, "excerpt_i18n", {}), locale),
            game_name=game_name_for_summary,
            limit=500,
        )
        summary = _clean_article_summary_text(
            _localize_article_field(instance.summary, getattr(instance, "summary_i18n", {}), locale),
            game_name=game_name_for_summary,
            limit=500,
        )
        content_text = _localize_article_field(instance.content, getattr(instance, "content_i18n", {}), locale)
        author_name = _localize_article_field(
            instance.author_name, getattr(instance, "author_name_i18n", {}), locale
        )
        read_time = _localize_article_field(instance.read_time, getattr(instance, "read_time_i18n", {}), locale)
        preview_content = content_text[:200] + "..." if len(content_text) > 200 else content_text
        category_name = _localized_category_name(getattr(instance, "category", None), locale)
        display_date = instance.published_at or instance.created_at

        return {
            "id": str(instance.id),
            "title": title,
            "excerpt": excerpt or summary or "",
            "summary": summary or excerpt or "",
            "content": preview_content,
            "image": image_url,
            "cover_image": image_url,
            "category": category_name,
            "category_name": category_name,
            "author": author_name,
            "author_name": author_name,
            "date": display_date.strftime("%Y-%m-%d") if display_date else "",
            "published_at": instance.published_at.isoformat() if instance.published_at else None,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "readTime": read_time,
            "read_time": read_time,
            "view_count": instance.view_count,
            "tags": self.get_tags(instance),
        }


class ArticleDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "category_name",
            "author_name",
            "cover_image",
            "excerpt",
            "content",
            "tags",
            "published_at",
            "read_time",
            "view_count",
        ]

    def get_tags(self, obj):
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        return [_localized_tag_name(tag, locale) for tag in obj.tags.all()]

    def _build_image_url(self, instance):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _resolve_article_image_url(instance, request=request)

    def to_representation(self, instance):
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        image_url = self._build_image_url(instance)
        title = _localize_article_field(instance.title, getattr(instance, "title_i18n", {}), locale)
        game_name_for_summary = str(getattr(getattr(instance, "game", None), "title", "") or "").strip()
        if not game_name_for_summary:
            game_name_for_summary = _normalize_game_keyword(title)
        excerpt = _clean_article_summary_text(
            _localize_article_field(instance.excerpt, getattr(instance, "excerpt_i18n", {}), locale),
            game_name=game_name_for_summary,
            limit=500,
        )
        summary = _clean_article_summary_text(
            _localize_article_field(instance.summary, getattr(instance, "summary_i18n", {}), locale),
            game_name=game_name_for_summary,
            limit=500,
        )
        content = _localize_article_field(instance.content, getattr(instance, "content_i18n", {}), locale)
        summary_seed = summary or excerpt
        if summary_seed and content:
            content = _normalize_existing_summary_block(
                content,
                locale=locale,
                summary_text=summary_seed,
                game_name=game_name_for_summary,
            )
        author_name = _localize_article_field(
            instance.author_name, getattr(instance, "author_name_i18n", {}), locale
        )
        read_time = _localize_article_field(instance.read_time, getattr(instance, "read_time_i18n", {}), locale)
        category_name = _localized_category_name(getattr(instance, "category", None), locale)
        display_date = instance.published_at or instance.created_at

        return {
            "id": str(instance.id),
            "title": title,
            "excerpt": excerpt or summary or "",
            "summary": summary or excerpt or "",
            "content": content,
            "image": image_url,
            "cover_image": image_url,
            "category": category_name,
            "category_name": category_name,
            "author": author_name,
            "author_name": author_name,
            "date": display_date.strftime("%Y-%m-%d") if display_date else "",
            "published_at": instance.published_at.isoformat() if instance.published_at else None,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "readTime": read_time,
            "read_time": read_time,
            "view_count": instance.view_count,
            "tags": self.get_tags(instance),
        }


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""

    user_name = serializers.CharField(source="user.username", read_only=True)
    article_title = serializers.CharField(source="article.title", read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "article_title",
            "user",
            "user_name",
            "parent",
            "content",
            "is_approved",
            "replies_count",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_replies_count(self, obj):
        return obj.replies.filter(is_approved=True).count()


class CommentDetailSerializer(serializers.ModelSerializer):
    """评论详情序列化器（含回复）"""

    user_name = serializers.CharField(source="user.username", read_only=True)
    article_title = serializers.CharField(source="article.title", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "article_title",
            "user",
            "user_name",
            "parent",
            "content",
            "is_approved",
            "replies",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True).order_by("created_at")
        return CommentSerializer(replies, many=True).data
