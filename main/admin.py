from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import HomeLayout, Banner, SiteConfig, MediaAsset
from .media_library import upsert_media_asset

# Register your models here.
admin.site.site_header = "运营管理系统"
admin.site.site_title = "运营看板"
admin.site.index_title = "管理后台"

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    change_list_template = "admin/main/mediaasset/change_list.html"
    list_display = ('preview_image', 'alt_text', 'created_at')
    list_editable = ('alt_text',)
    list_filter = ('created_at',)
    search_fields = ('name', 'alt_text')
    readonly_fields = ('file_size', 'created_at', 'updated_at', 'preview_image_large')
    list_per_page = 20

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload/', self.admin_site.admin_view(self.upload_images), name='media-upload'),
        ]
        return custom_urls + urls

    def upload_images(self, request):
        from django.http import JsonResponse
        
        if request.method == 'POST':
            files = request.FILES.getlist('file')
            uploaded_count = 0
            deduped_count = 0
            errors: list[str] = []
            
            for file_obj in files:
                try:
                    _instance, created = upsert_media_asset(
                        file_obj=file_obj,
                        requested_name=getattr(file_obj, "name", ""),
                        category='other',
                        alt_text='',
                        create_thumbnail=True,
                    )
                    if created:
                        uploaded_count += 1
                    else:
                        deduped_count += 1
                except Exception as e:
                    errors.append(f"{getattr(file_obj, 'name', 'unknown')}: {str(e)}")
            
            return JsonResponse(
                {
                    'status': 'success',
                    'count': uploaded_count,
                    'deduped_count': deduped_count,
                    'error_count': len(errors),
                    'errors': errors[:10],
                }
            )
        
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    def preview_image(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #eee;" />')
        elif obj.file:
            return mark_safe(f'<img src="{obj.file.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #eee;" />')
        return "-"
    preview_image.short_description = "图片预览"

    def preview_image_large(self, obj):
        if obj.file:
            return mark_safe(f'<img src="{obj.file.url}" style="max-width: 300px; max-height: 300px; border-radius: 4px;" />')
        return "-"
    preview_image_large.short_description = "大图预览"


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'is_maintenance_mode', 'updated_at')
    
    class Media:
        js = ('admin/js/media_picker_widget.js',)
        css = {
            'all': ('admin/css/media_picker.css',)
        }
    
    def has_add_permission(self, request):
        # 只能有一条记录，如果已经存在则不能添加
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # 禁止删除配置
        return False

@admin.register(HomeLayout)
class HomeLayoutAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'section_key', 'is_enabled', 'sort_order', 'view_count', 'updated_at')
    list_editable = ('is_enabled', 'sort_order')
    list_filter = ('is_enabled', 'section_key')
    search_fields = ('section_name', 'section_key')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_default', 'sort_order', 'view_count', 'click_count', 'updated_at')
    list_editable = ('status', 'is_default', 'sort_order')
    list_filter = ('status', 'is_default')
    search_fields = ('title', 'description')
    
    class Media:
        js = ('admin/js/media_picker_widget.js',)
        css = {
            'all': ('admin/css/media_picker.css',)
        }
