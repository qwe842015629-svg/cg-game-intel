import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.html import format_html, format_html_join
from django.utils.text import slugify

from .models import Article, ArticleCategory, ArticleTag, Comment


class ArticleAdminForm(forms.ModelForm):
    """资讯文章后台编辑表单。"""

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 24,
                "class": "editor-textarea editor-textarea--xl",
                "placeholder": "支持 Markdown / HTML，建议使用标题和分段提升可读性。",
            }
        ),
        label="文章内容",
        help_text="支持 Markdown 与 HTML。",
    )

    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "excerpt": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "editor-textarea",
                    "placeholder": "用于列表页摘要（建议 80~140 字）。",
                    "data-char-counter": "500",
                }
            ),
            "summary": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "editor-textarea",
                    "placeholder": "用于详情页导语（可与摘要不同）。",
                    "data-char-counter": "500",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "editor-textarea",
                    "placeholder": "SEO 描述建议 70~160 字。",
                    "data-char-counter": "300",
                }
            ),
            "meta_keywords": forms.TextInput(
                attrs={
                    "placeholder": "示例：手游充值,游戏攻略,资讯",
                    "data-char-counter": "200",
                }
            ),
            "title": forms.TextInput(attrs={"data-char-counter": "200"}),
            "meta_title": forms.TextInput(attrs={"data-char-counter": "200"}),
        }


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "articles_count", "sort_order", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["sort_order", "is_active"]
    ordering = ["sort_order"]

    def articles_count(self, obj):
        count = obj.articles.filter(status="published").count()
        return format_html('<span class="admin-list-number">{}</span>', count)

    articles_count.short_description = "已发布文章数"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    change_form_template = "admin/game_article/change_form.html"

    list_display = [
        "cover_thumb",
        "title_display",
        "category",
        "game",
        "author_name",
        "status_display",
        "is_top",
        "is_hot",
        "is_recommended",
        "view_count_display",
        "published_at",
        "created_at",
    ]
    list_display_links = ["title_display"]
    list_filter = [
        "category",
        "game",
        "status",
        "is_top",
        "is_hot",
        "is_recommended",
        "created_at",
        "published_at",
    ]
    search_fields = ["title", "content", "author_name", "meta_keywords", "slug"]
    search_help_text = "支持按标题、作者、关键词或 slug 搜索"
    list_editable = ["is_top", "is_hot", "is_recommended"]
    readonly_fields = [
        "cover_preview",
        "view_count",
        "like_count",
        "comment_count",
        "created_at",
        "updated_at",
        "preview_link",
    ]
    filter_horizontal = ["tags"]
    date_hierarchy = "published_at"
    list_per_page = 20
    save_on_top = True

    fieldsets = (
        (
            "基础信息",
            {
                "fields": (
                    ("title", "slug"),
                    ("category", "game"),
                    ("author", "author_name"),
                    ("cover_image", "cover_preview"),
                )
            },
        ),
        (
            "内容编辑",
            {
                "fields": (
                    ("excerpt", "summary"),
                    "content",
                    "read_time",
                ),
                "classes": ("wide",),
                "description": "支持 Markdown/HTML；建议段落不超过 4 行并配图增强阅读体验。",
            },
        ),
        (
            "SEO 优化",
            {
                "fields": (
                    ("meta_title", "meta_keywords"),
                    "meta_description",
                ),
                "classes": ("collapse",),
            },
        ),
        ("标签", {"fields": ("tags",)}),
        (
            "发布设置",
            {
                "fields": (
                    ("status", "published_at"),
                    ("is_top", "is_hot", "is_recommended"),
                    "preview_link",
                )
            },
        ),
        (
            "统计信息",
            {
                "fields": (
                    ("view_count", "like_count", "comment_count"),
                    ("created_at", "updated_at"),
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" class="admin-list-thumb admin-list-thumb--article" alt="cover" '
                'style="width:56px;height:56px;max-width:56px;max-height:56px;display:block;object-fit:cover;border-radius:10px;border:1px solid #dbeafe;"/>',
                obj.cover_image.url,
            )
        return format_html('<span class="admin-list-muted">无封面</span>')

    cover_thumb.short_description = "封面"

    def cover_preview(self, obj):
        preview_id = "article-cover-live-preview"
        if obj.cover_image:
            return format_html(
                '<div id="{}" class="admin-image-preview-card">'
                '<img src="{}" alt="封面预览" class="admin-image-preview-card__img"/>'
                '<div class="admin-image-preview-card__meta">当前封面：{}</div>'
                "</div>",
                preview_id,
                obj.cover_image.url,
                obj.cover_image.name.split("/")[-1],
            )
        return format_html(
            '<div id="{}" class="admin-image-preview-card admin-image-preview-card--empty">未上传封面图片</div>',
            preview_id,
        )

    cover_preview.short_description = "封面预览"

    def title_display(self, obj):
        title = obj.title[:48] + "..." if len(obj.title) > 48 else obj.title

        badge_items = []
        if obj.is_top:
            badge_items.append(("admin-list-badge--top", "置顶"))
        if obj.is_hot:
            badge_items.append(("admin-list-badge--hot", "热门"))
        if obj.is_recommended:
            badge_items.append(("admin-list-badge--rec", "推荐"))

        badges = ""
        if badge_items:
            badges = format_html_join(
                "",
                '<span class="admin-list-badge {}">{}</span>',
                ((css_class, text) for css_class, text in badge_items),
            )

        return format_html(
            '<div class="admin-list-title-wrap"><span class="admin-list-title">{}</span>{}</div>',
            title,
            badges,
        )

    title_display.short_description = "标题"

    def status_display(self, obj):
        status_text = dict(Article.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span class="admin-list-status admin-list-status--{}">{}</span>',
            obj.status,
            status_text,
        )

    status_display.short_description = "状态"

    def view_count_display(self, obj):
        return format_html('<span class="admin-list-number">{}</span>', obj.view_count)

    view_count_display.short_description = "浏览量"

    def preview_link(self, obj):
        if obj.pk:
            return format_html(
                '<a href="/zh-CN/articles/{}" target="_blank" rel="noopener" style="color:#2563eb;">打开前台预览</a>',
                obj.id,
            )
        return "-"

    preview_link.short_description = "预览链接"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user

        if not obj.meta_title:
            obj.meta_title = obj.title

        if not obj.meta_description and obj.excerpt:
            obj.meta_description = obj.excerpt[:300]

        if not obj.slug:
            obj.slug = f"{slugify(obj.title[:50])}-{uuid.uuid4().hex[:8]}"

        self._apply_cover_from_content_selection(request, obj)
        super().save_model(request, obj, form, change)

    def _apply_cover_from_content_selection(self, request, obj):
        """Use selected content image URL as cover when no local upload is provided."""
        if request.FILES.get("cover_image"):
            return

        source_url = str(request.POST.get("cover_image_from_content_url") or "").strip()
        if not source_url:
            return

        try:
            req = Request(source_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=20) as resp:
                raw = resp.read()
        except Exception as exc:
            messages.warning(request, f"从正文选择封面失败：无法下载图片（{exc}）")
            return

        if not raw:
            messages.warning(request, "从正文选择封面失败：图片内容为空")
            return

        parsed = urlparse(source_url)
        ext = Path(parsed.path).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif"}:
            ext = ".jpg"

        stem = slugify((obj.title or "article-cover")[:60]) or "article-cover"
        filename = f"{stem}-{uuid.uuid4().hex[:8]}{ext}"
        obj.cover_image.save(filename, ContentFile(raw), save=False)

    class Media:
        css = {
            "all": (
                "admin/css/media_picker.css",
                "admin/css/editor_admin.css",
                "admin/css/article_admin.css",
                "admin/css/editor_admin_list.css",
                "admin/css/uai_editor_bridge_v2.css",
            )
        }
        js = (
            "admin/js/media_picker_widget.js",
            "admin/js/editor_admin.js",
            "admin/js/article_admin.js",
            "admin/js/editor_admin_list.js",
            "admin/js/uai_editor_bridge_v2.js",
        )


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ["name", "articles_count", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]

    def articles_count(self, obj):
        count = obj.articles.filter(status="published").count()
        return format_html('<span class="admin-list-number">{}</span>', count)

    articles_count.short_description = "已发布文章数"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "article_title",
        "user_name",
        "content_preview",
        "parent_preview",
        "is_approved",
        "created_at",
    ]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["content", "user__username", "article__title"]
    list_editable = ["is_approved"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["article", "user", "parent"]
    list_per_page = 50

    def article_title(self, obj):
        return obj.article.title[:30] + "..." if len(obj.article.title) > 30 else obj.article.title

    article_title.short_description = "文章"

    def user_name(self, obj):
        return format_html("<strong>{}</strong>", obj.user.username)

    user_name.short_description = "用户"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "评论内容"

    def parent_preview(self, obj):
        if obj.parent:
            return obj.parent.content[:30] + "..."
        return "-"

    parent_preview.short_description = "回复自"
