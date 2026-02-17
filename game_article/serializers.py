import re
from urllib.parse import quote

from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers

from game_page.models import GamePage
from .models import Article, ArticleCategory, ArticleTag, Comment


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


def _normalize_game_keyword(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return ""
    text = re.sub(r"[|｜:：\-—_].*$", "", text).strip()
    text = re.sub(r"(攻略|教學|教程|心得|懶人包|新手|版本|玩法|儲值|充值|代儲).*$", "", text).strip()
    return text


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


def _build_related_links_block(instance: Article) -> str:
    related_game = _resolve_related_game_for_article(instance)
    game_name = (
        str(getattr(related_game, "title", "") or "").strip()
        or _normalize_game_keyword(getattr(instance, "title", ""))
        or "游戏"
    )

    if related_game:
        internal_href = f"/games/{related_game.id}"
    else:
        internal_href = f"/games?keyword={quote(game_name, safe='')}"

    if related_game and str(getattr(related_game, "google_play_id", "") or "").strip():
        google_href = (
            "https://play.google.com/store/apps/details"
            f"?id={quote(str(related_game.google_play_id).strip(), safe='')}"
        )
    else:
        google_href = f"https://play.google.com/store/search?q={quote(game_name, safe='')}&c=apps"

    apple_href = f"https://apps.apple.com/tw/iphone/search?term={quote(game_name, safe='')}"

    label = game_name
    return (
        '<section class="seo-related-links">'
        "<h2>相關遊戲與官方連結</h2>"
        "<p>想继续推进进度时，先确认版本、区服与账号资讯，会更稳定。</p>"
        "<ul>"
        f'<li>🧭 <a href="{internal_href}" target="_blank" rel="noopener">本站游戏详情：{label}</a></li>'
        f'<li>🎮 <a href="{google_href}" target="_blank" rel="noopener noreferrer">Google Play 下载页：{label}</a></li>'
        f'<li>🍎 <a href="{apple_href}" target="_blank" rel="noopener noreferrer">App Store 搜索页：{label}</a></li>'
        "</ul>"
        '<p class="seo-recharge-note">需要补资源时，可直接在本站对应游戏页完成操作与记录核对，流程更顺。</p>'
        "</section>"
    )


def _ensure_related_links_block(content: str, instance: Article) -> str:
    body = str(content or "")
    if "seo-related-links" in body or "相關遊戲與官方連結" in body or "相关游戏与官方链接" in body:
        return body
    return body + _build_related_links_block(instance)


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


class ArticleTagSerializer(serializers.ModelSerializer):
    """文章标签序列化器"""

    class Meta:
        model = ArticleTag
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]


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
        return obj.get_tags_list()

    def _build_image_url(self, instance):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _resolve_article_image_url(instance, request=request)

    def to_representation(self, instance):
        image_url = self._build_image_url(instance)
        content_text = instance.content or ""
        preview_content = content_text[:200] + "..." if len(content_text) > 200 else content_text
        category_name = instance.category.name if instance.category else "游戏资讯"
        display_date = instance.published_at or instance.created_at

        return {
            "id": str(instance.id),
            "title": instance.title,
            "excerpt": instance.excerpt or instance.summary or "",
            "summary": instance.summary or instance.excerpt or "",
            "content": preview_content,
            "image": image_url,
            "cover_image": image_url,
            "category": category_name,
            "category_name": category_name,
            "author": instance.author_name,
            "author_name": instance.author_name,
            "date": display_date.strftime("%Y-%m-%d") if display_date else "",
            "published_at": instance.published_at.isoformat() if instance.published_at else None,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "readTime": instance.read_time,
            "read_time": instance.read_time,
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
        return obj.get_tags_list()

    def _build_image_url(self, instance):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _resolve_article_image_url(instance, request=request)

    def to_representation(self, instance):
        image_url = self._build_image_url(instance)
        category_name = instance.category.name if instance.category else "游戏资讯"
        display_date = instance.published_at or instance.created_at
        content = _ensure_related_links_block(instance.content or "", instance)

        return {
            "id": str(instance.id),
            "title": instance.title,
            "excerpt": instance.excerpt or instance.summary or "",
            "summary": instance.summary or instance.excerpt or "",
            "content": content,
            "image": image_url,
            "cover_image": image_url,
            "category": category_name,
            "category_name": category_name,
            "author": instance.author_name,
            "author_name": instance.author_name,
            "date": display_date.strftime("%Y-%m-%d") if display_date else "",
            "published_at": instance.published_at.isoformat() if instance.published_at else None,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "readTime": instance.read_time,
            "read_time": instance.read_time,
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
