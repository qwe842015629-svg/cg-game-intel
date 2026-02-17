import logging
import json

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
    """自定义游戏页面表单，支持富文本编辑"""

    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'style': 'width: 100%; font-family: monospace;'}),
        label='游戏详情',
        required=False,
    )
    content_tw = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'style': 'width: 100%; font-family: monospace;'}),
        label='游戏详情(繁体)',
        required=False,
    )
    topup_info = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'style': 'width: 100%; font-family: monospace;'}),
        label='充值说明',
        required=False,
    )
    topup_info_tw = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'style': 'width: 100%; font-family: monospace;'}),
        label='充值说明(繁体)',
        required=False,
    )

    class Meta:
        model = GamePage
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
            'description_tw': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
            'seo_description': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
        }


@admin.register(GamePageCategory)
class GamePageCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'pages_count', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order']

    def pages_count(self, obj):
        """显示游戏页面数量"""
        count = obj.games.filter(status='published').count()
        return format_html('<span style="color: #00a854;">{}</span>', count)

    pages_count.short_description = '游戏数'


@admin.register(GamePageTemplate)
class GamePageTemplateAdmin(admin.ModelAdmin):
    list_display = ["key", "updated_at", "created_at"]
    search_fields = ["key", "topup_info", "topup_info_tw"]
    ordering = ["key"]


@admin.register(GamePage)
class GamePageAdmin(admin.ModelAdmin):
    form = GamePageAdminForm
    change_form_template = 'admin/game_page/change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('scrape-google-play/', self.admin_site.admin_view(self.scrape_google_play), name='scrape-google-play'),
            path('topup-template/list/', self.admin_site.admin_view(self.topup_template_list), name='topup-template-list'),
            path('topup-template/load/', self.admin_site.admin_view(self.topup_template_load), name='topup-template-load'),
            path('topup-template/save/', self.admin_site.admin_view(self.topup_template_save), name='topup-template-save'),
        ]
        return custom_urls + urls

    def scrape_google_play(self, request):
        """处理 Google Play 抓取请求"""
        url = request.GET.get('url')
        if not url:
            return JsonResponse({'error': '请提供 Google Play 链接'}, status=400)

        scraper = GooglePlayScraper()
        data = scraper.fetch_game_info(url)
        if 'error' in data:
            return JsonResponse(data, status=400)

        icon_url = data.get('icon_url') or ''
        data['icon_external_url'] = icon_url
        data['icon_sync_status'] = 'none'

        # 提取时即尝试下载图标到素材库，方便后续自动绑定本地图片
        if icon_url:
            media = scraper.save_icon_to_media_library(
                icon_url,
                data.get('title') or '',
                package_id=data.get('package_id') or '',
            )
            if media:
                data['media_id'] = media.id
                data['media_url'] = media.file.url
                data['icon_sync_status'] = 'downloaded'
            else:
                data['icon_sync_status'] = 'external_only'

        return JsonResponse(data)


    def topup_template_list(self, request):
        if request.method != "GET":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        rows = (
            GamePageTemplate.objects.all()
            .order_by("key")
            .values("key", "updated_at")
        )
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
        return JsonResponse(
            {
                "status": "created" if created else "updated",
                "key": template.key,
            }
        )

    list_display = [
        'title_display',
        'category',
        'platform',
        'regions',
        'status_display',
        'is_hot',
        'is_recommended',
        'sort_order',
        'view_count_display',
        'published_at',
        'created_at',
    ]

    readonly_fields = [
        'view_count',
        'like_count',
        'created_at',
        'updated_at',
        'preview_link',
    ]

    fieldsets = (
        ('快速导入', {
            'fields': (),
            'description': '<div style="display:flex; gap:10px; align-items:center;">'
            '<input type="text" id="google-play-url" class="vTextField" placeholder="输入 Google Play 链接 (例如: https://play.google.com/store/apps/details?id=...)" style="width:400px;">'
            '<span id="scrape-btn" class="button" style="cursor:pointer; background:#2f80ed; color:white; border:none;">📥 从 Google Play 导入</span>'
            '<span id="scrape-status" style="margin-left:10px; color:#666;"></span>'
            '</div>',
        }),
        ('基础信息', {
            'fields': ('title', 'title_tw', 'slug', 'category', 'icon_image', 'icon_external_url', 'banner_image', 'author')
        }),
        ('游戏参数', {
            'fields': ('developer', 'platform', 'regions', 'server_name', 'google_play_id'),
            'classes': ('wide',)
        }),
        ('详情内容 (简体)', {
            'fields': ('description', 'content', 'topup_info'),
            'classes': ('wide',),
        }),
        ('详情内容 (繁体)', {
            'fields': ('description_tw', 'content_tw', 'topup_info_tw'),
            'classes': ('collapse',),
        }),
        ('SEO 优化 (港台)', {
            'fields': ('seo_title', 'seo_keywords', 'seo_description'),
            'classes': ('wide',),
            'description': '一键生成的 SEO 信息将根据游戏名称自动填充，也可手动修改。',
        }),
        ('发布设置', {
            'fields': (
                'status',
                'sort_order',
                'is_hot',
                'is_recommended',
                'published_at',
                'preview_link',
            ),
        }),
    )

    class Media:
        js = (
            'admin/js/media_picker_widget.js',
            'admin/js/google_play_scraper.js',
            'admin/js/gamepage_topup_templates.js',
        )
        css = {
            'all': ('admin/css/media_picker.css',)
        }

    def title_display(self, obj):
        """Display game title with badges."""
        raw_title = str(getattr(obj, 'title', '') or '')
        clean_title = strip_tags(raw_title).strip()
        title = clean_title[:30] + '...' if len(clean_title) > 30 else clean_title

        badge_items: list[tuple[str, str]] = []
        if obj.is_hot:
            badge_items.append(('#ff5722', 'HOT'))
        if obj.is_recommended:
            badge_items.append(('#2196f3', 'REC'))

        badges = ''
        if badge_items:
            badges = format_html_join(
                '',
                '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">{}</span>',
                ((color, label) for color, label in badge_items),
            )

        external_icon_url = getattr(obj, 'icon_external_url', '') or ''
        icon_src = obj.icon_image.url if obj.icon_image else (external_icon_url or '/static/default_icon.png')
        return format_html(
            '<div style="display:flex; align-items:center;">'
            '<img src="{}" style="width:24px; height:24px; border-radius:4px; margin-right:8px; object-fit:cover;">'
            '<span>{}</span>{}'
            '</div>',
            icon_src,
            title,
            badges,
        )

    title_display.short_description = 'Game Name'


    def status_display(self, obj):
        """显示状态彩色标签"""
        status_colors = {
            'draft': '#999',
            'published': '#52c41a',
            'archived': '#faad14',
        }
        status_text = dict(GamePage.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            status_colors.get(obj.status, '#999'),
            status_text,
        )

    status_display.short_description = '状态'

    def view_count_display(self, obj):
        """显示浏览量"""
        return format_html('<strong style="color: #1890ff;">{}</strong>', obj.view_count)

    view_count_display.short_description = '浏览'

    def preview_link(self, obj):
        """预览链接"""
        if obj.pk:
            return format_html(
                '<a href="/games/{}" target="_blank" style="color: #1890ff;">预览页面</a>',
                obj.slug or obj.id,
            )
        return '-'

    preview_link.short_description = '预览'

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user

        # 自动填充发布时间：如果状态是已发布且没有发布时间，则设为当前时间
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)

        # 兜底：保存时自动把外链图标同步进素材库并绑定 icon_image
        external_icon_url = getattr(obj, 'icon_external_url', '') or ''
        if not obj.icon_image and external_icon_url:
            try:
                scraper = GooglePlayScraper()
                media = scraper.save_icon_to_media_library(
                    external_icon_url,
                    obj.title or '',
                    package_id=obj.google_play_id or '',
                )
                if media and media.file:
                    obj.icon_image = media.file
                    obj.save(update_fields=['icon_image', 'updated_at'])
            except Exception as exc:
                logger.warning('Auto sync icon failed for GamePage(id=%s): %s', obj.pk, exc)
