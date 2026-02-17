from django.contrib import admin
from .models import FooterSection, FooterLink, FooterConfig


class FooterLinkInline(admin.TabularInline):
    """底部链接内联编辑"""
    model = FooterLink
    extra = 1
    fields = ['title', 'url', 'icon', 'is_external', 'is_active', 'sort_order']


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    """页面底部板块管理"""
    list_display = ['section_type', 'title', 'is_active', 'sort_order', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['section_type', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['sort_order', 'id']
    inlines = [FooterLinkInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('section_type', 'title', 'description')
        }),
        ('状态', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    """底部链接管理"""
    list_display = ['section', 'title', 'url', 'is_external', 'is_active', 'sort_order', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['section', 'is_external', 'is_active']
    search_fields = ['title', 'url']
    ordering = ['section', 'sort_order', 'id']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('section', 'title', 'url', 'icon')
        }),
        ('设置', {
            'fields': ('is_external', 'is_active', 'sort_order')
        }),
    )


@admin.register(FooterConfig)
class FooterConfigAdmin(admin.ModelAdmin):
    """页面底部配置管理"""
    list_display = ['copyright_text', 'show_copyright', 'updated_at']
    
    fieldsets = (
        ('版权信息', {
            'fields': ('copyright_text', 'show_copyright')
        }),
    )
    
    def has_add_permission(self, request):
        # 只允许有一条配置记录
        return not FooterConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # 不允许删除配置
        return False
