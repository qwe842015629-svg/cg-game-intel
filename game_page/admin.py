import json
import logging

from django import forms
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html, format_html_join, strip_tags

from .models import GamePage, GamePageCategory, GamePageTemplate
from .scraper import GooglePlayScraper

logger = logging.getLogger(__name__)


class GamePageAdminForm(forms.ModelForm):
    """游戏页面后台编辑表单。"""

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 20,
                "class": "editor-textarea editor-textarea--xl",
                "placeholder": "游戏详情（简体），支持 Markdown / HTML。",
            }
        ),
        label="游戏详情",
        required=False,
    )
    content_tw = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 20,
                "class": "editor-textarea editor-textarea--xl",
                "placeholder": "游戏详情（繁体），支持 Markdown / HTML。",
            }
        ),
        label="游戏详情（繁体）",
        required=False,
    )
    topup_info = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "class": "editor-textarea editor-textarea--lg",
                "placeholder": "充值说明（简体）。",
            }
        ),
        label="充值说明",
        required=False,
    )
    topup_info_tw = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "class": "editor-textarea editor-textarea--lg",
                "placeholder": "充值说明（繁体）。",
            }
        ),
        label="充值说明（繁体）",
        required=False,
    )

    class Meta:
        model = GamePage
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4, "class": "editor-textarea", "data-char-counter": "500"}
            ),
            "description_tw": forms.Textarea(
                attrs={"rows": 4, "class": "editor-textarea", "data-char-counter": "500"}
            ),
            "seo_description": forms.Textarea(
                attrs={"rows": 4, "class": "editor-textarea", "data-char-counter": "500"}
            ),
            "title": forms.TextInput(attrs={"data-char-counter": "200"}),
            "title_tw": forms.TextInput(attrs={"data-char-counter": "200"}),
            "seo_title": forms.TextInput(attrs={"data-char-counter": "200"}),
            "seo_keywords": forms.TextInput(attrs={"data-char-counter": "200"}),
        }


@admin.register(GamePageCategory)
class GamePageCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "pages_count", "sort_order", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["sort_order", "is_active"]
    ordering = ["sort_order"]

    def pages_count(self, obj):
        count = obj.games.filter(status="published").count()
        return format_html('<span class="admin-list-number">{}</span>', count)

    pages_count.short_description = "已发布游戏数"


@admin.register(GamePageTemplate)
class GamePageTemplateAdmin(admin.ModelAdmin):
    list_display = ["key", "updated_at", "created_at"]
    search_fields = ["key", "topup_info", "topup_info_tw"]
    ordering = ["key"]


@admin.register(GamePage)
class GamePageAdmin(admin.ModelAdmin):
    form = GamePageAdminForm
    change_form_template = "admin/game_page/change_form.html"

    list_display = [
        "title_display",
        "category",
        "platform",
        "regions",
        "status_display",
        "is_hot",
        "is_recommended",
        "sort_order",
        "view_count_display",
        "published_at",
        "created_at",
    ]
    list_display_links = ["title_display"]
    list_filter = ["category", "status", "is_hot", "is_recommended", "published_at", "created_at"]
    search_fields = ["title", "title_tw", "developer", "google_play_id", "slug"]
    search_help_text = "支持按标题、开发商、Google Play ID 或 slug 搜索"
    list_editable = ["is_hot", "is_recommended", "sort_order"]
    date_hierarchy = "published_at"
    list_per_page = 20
    save_on_top = True
    readonly_fields = [
        "icon_preview",
        "banner_preview",
        "view_count",
        "like_count",
        "created_at",
        "updated_at",
        "preview_link",
    ]

    fieldsets = (
        (
            "快速导入",
            {
                "fields": (),
                "description": (
                    '<div class="admin-quick-import">'
                    '<input type="text" id="google-play-url" class="vTextField admin-quick-import__input" '
                    'placeholder="粘贴 Google Play 链接（例如 https://play.google.com/store/apps/details?id=...）">'
                    '<span id="scrape-btn" class="button admin-quick-import__btn">从 Google Play 导入</span>'
                    '<span id="scrape-status" class="admin-quick-import__status"></span>'
                    "</div>"
                ),
            },
        ),
        (
            "基础信息",
            {
                "fields": (
                    ("title", "title_tw"),
                    ("slug",),
                    ("category", "author"),
                    ("icon_image", "icon_preview"),
                    "icon_external_url",
                    ("banner_image", "banner_preview"),
                )
            },
        ),
        (
            "游戏参数",
            {
                "fields": (
                    ("developer", "google_play_id"),
                    ("platform", "regions"),
                    ("server_name",),
                ),
                "classes": ("wide",),
            },
        ),
        (
            "详情内容（简体）",
            {
                "fields": ("description", "content", "topup_info"),
                "classes": ("wide",),
            },
        ),
        (
            "详情内容（繁体）",
            {
                "fields": ("description_tw", "content_tw", "topup_info_tw"),
                "classes": ("collapse",),
            },
        ),
        (
            "SEO 优化",
            {
                "fields": (
                    ("seo_title", "seo_keywords"),
                    "seo_description",
                ),
                "classes": ("wide",),
                "description": "默认会按游戏名称自动生成，可手动覆盖。",
            },
        ),
        (
            "发布设置",
            {
                "fields": (
                    ("status", "published_at"),
                    ("sort_order", "is_hot", "is_recommended"),
                    "preview_link",
                )
            },
        ),
    )

    class Media:
        js = (
            "admin/js/media_picker_widget.js",
            "admin/js/google_play_scraper_v6.js",
            "admin/js/gamepage_topup_templates.js",
            "admin/js/gamepage_content_enhancer.js",
            "admin/js/editor_admin.js",
            "admin/js/editor_admin_list.js",
            "admin/js/uai_editor_bridge_v2.js",
        )
        css = {
            "all": (
                "admin/css/media_picker.css",
                "admin/css/editor_admin.css",
                "admin/css/editor_admin_list.css",
                "admin/css/uai_editor_bridge_v2.css",
            )
        }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("scrape-google-play/", self.admin_site.admin_view(self.scrape_google_play), name="scrape-google-play"),
            path("topup-template/list/", self.admin_site.admin_view(self.topup_template_list), name="topup-template-list"),
            path("topup-template/load/", self.admin_site.admin_view(self.topup_template_load), name="topup-template-load"),
            path("topup-template/save/", self.admin_site.admin_view(self.topup_template_save), name="topup-template-save"),
        ]
        return custom_urls + urls

    def scrape_google_play(self, request):
        url = request.GET.get("url")
        if not url:
            return JsonResponse({"error": "请提供 Google Play 链接"}, status=400)

        scraper = GooglePlayScraper()
        data = scraper.fetch_game_info(url)
        if "error" in data:
            return JsonResponse(data, status=400)

        icon_url = data.get("icon_url") or ""
        data["icon_external_url"] = icon_url
        data["icon_sync_status"] = "none"

        if icon_url:
            media = scraper.save_icon_to_media_library(
                icon_url,
                data.get("title") or "",
                package_id=data.get("package_id") or "",
            )
            if media:
                data["media_id"] = media.id
                data["media_url"] = media.file.url
                data["icon_sync_status"] = "downloaded"
            else:
                data["icon_sync_status"] = "external_only"

        return JsonResponse(data)

    def topup_template_list(self, request):
        if request.method != "GET":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        rows = GamePageTemplate.objects.all().order_by("key").values("key", "updated_at")
        items = [
            {
                "key": str(row.get("key") or ""),
                "updated_at": row.get("updated_at").isoformat() if row.get("updated_at") else "",
            }
            for row in rows
        ]
        return JsonResponse({"items": items})

    def topup_template_load(self, request):
        if request.method != "GET":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        key = str(request.GET.get("key") or "").strip()
        if not key:
            return JsonResponse({"error": "Template key is required"}, status=400)

        template = GamePageTemplate.objects.filter(key=key).first()
        if template is None:
            return JsonResponse({"error": f"Template not found: {key}"}, status=404)

        return JsonResponse(
            {
                "key": template.key,
                "topup_info": template.topup_info or "",
                "topup_info_tw": template.topup_info_tw or "",
            }
        )

    def topup_template_save(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        payload: dict = {}
        body = request.body.decode("utf-8", errors="ignore").strip() if request.body else ""
        if body:
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    payload = parsed
            except Exception:
                payload = {}

        key = str(payload.get("key") or request.POST.get("key") or "").strip().lower()
        if not key:
            key = "default"
        key = key[:50]
        if not key:
            return JsonResponse({"error": "Template key is required"}, status=400)

        topup_info = str(payload.get("topup_info") or request.POST.get("topup_info") or "")
        topup_info_tw = str(payload.get("topup_info_tw") or request.POST.get("topup_info_tw") or "")
        if not topup_info.strip() and not topup_info_tw.strip():
            return JsonResponse({"error": "Template content is empty"}, status=400)

        template, created = GamePageTemplate.objects.update_or_create(
            key=key,
            defaults={
                "topup_info": topup_info,
                "topup_info_tw": topup_info_tw,
            },
        )
        return JsonResponse({"status": "created" if created else "updated", "key": template.key})

    def title_display(self, obj):
        raw_title = str(getattr(obj, "title", "") or "")
        clean_title = strip_tags(raw_title).strip()
        title = clean_title[:30] + "..." if len(clean_title) > 30 else clean_title

        badge_items: list[tuple[str, str]] = []
        if obj.is_hot:
            badge_items.append(("admin-list-badge--hot", "HOT"))
        if obj.is_recommended:
            badge_items.append(("admin-list-badge--rec", "REC"))

        badges = ""
        if badge_items:
            badges = format_html_join(
                "",
                '<span class="admin-list-badge {}">{}</span>',
                ((css_class, label) for css_class, label in badge_items),
            )

        external_icon_url = getattr(obj, "icon_external_url", "") or ""
        icon_src = obj.icon_image.url if obj.icon_image else (external_icon_url or "/static/default_icon.png")
        return format_html(
            '<div class="admin-list-title-wrap">'
            '<img src="{}" class="admin-list-thumb admin-list-thumb--icon" alt="icon" '
            'style="width:28px;height:28px;max-width:28px;max-height:28px;display:block;object-fit:cover;border-radius:7px;border:1px solid #dbeafe;"/>'
            '<span class="admin-list-title">{}</span>{}'
            "</div>",
            icon_src,
            title,
            badges,
        )

    title_display.short_description = "游戏名"

    def status_display(self, obj):
        status_text = dict(GamePage.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span class="admin-list-status admin-list-status--{}">{}</span>',
            obj.status,
            status_text,
        )

    status_display.short_description = "状态"

    def view_count_display(self, obj):
        return format_html('<span class="admin-list-number">{}</span>', obj.view_count)

    view_count_display.short_description = "浏览"

    def icon_preview(self, obj):
        preview_id = "gamepage-icon-live-preview"
        local_url = obj.icon_image.url if obj.icon_image else ""
        external_url = (obj.icon_external_url or "").strip()
        if local_url or external_url:
            effective_url = local_url or external_url
            source = "本地图标" if local_url else "外链图标（兜底）"
            return format_html(
                '<div id="{}" class="admin-image-preview-card" style="max-width:360px;">'
                '<img src="{}" alt="图标预览" class="admin-image-preview-card__img admin-image-preview-card__img--icon" '
                'style="width:96px;height:96px;max-width:96px;max-height:96px;display:block;object-fit:cover;margin:14px auto 0;border-radius:14px;border:1px solid #dbeafe;"/>'
                '<div class="admin-image-preview-card__meta" style="text-align:center;">{}</div>'
                "</div>",
                preview_id,
                effective_url,
                source,
            )
        return format_html(
            '<div id="{}" class="admin-image-preview-card admin-image-preview-card--empty">未上传图标</div>',
            preview_id,
        )

    icon_preview.short_description = "图标预览"

    def banner_preview(self, obj):
        preview_id = "gamepage-banner-live-preview"
        if obj.banner_image:
            return format_html(
                '<div id="{}" class="admin-image-preview-card" style="max-width:520px;">'
                '<img src="{}" alt="Banner 预览" class="admin-image-preview-card__img admin-image-preview-card__img--banner" '
                'style="width:100%;height:180px;max-height:180px;display:block;object-fit:cover;"/>'
                '<div class="admin-image-preview-card__meta">当前 Banner：{}</div>'
                "</div>",
                preview_id,
                obj.banner_image.url,
                obj.banner_image.name.split("/")[-1],
            )
        return format_html(
            '<div id="{}" class="admin-image-preview-card admin-image-preview-card--empty">未上传 Banner</div>',
            preview_id,
        )

    banner_preview.short_description = "Banner 预览"

    def preview_link(self, obj):
        if obj.pk:
            return format_html(
                '<a href="/games/{}" target="_blank" rel="noopener" style="color:#1890ff;">打开前台预览</a>',
                obj.slug or obj.id,
            )
        return "-"

    preview_link.short_description = "预览"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user

        if obj.status == "published" and not obj.published_at:
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)

        external_icon_url = getattr(obj, "icon_external_url", "") or ""
        if not obj.icon_image and external_icon_url:
            try:
                scraper = GooglePlayScraper()
                media = scraper.save_icon_to_media_library(
                    external_icon_url,
                    obj.title or "",
                    package_id=obj.google_play_id or "",
                )
                if media and media.file:
                    obj.icon_image = media.file
                    obj.save(update_fields=["icon_image", "updated_at"])
            except Exception as exc:
                logger.warning("Auto sync icon failed for GamePage(id=%s): %s", obj.pk, exc)
