from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import ProductShowCategory, ProductShow


class ProductShowAdminForm(forms.ModelForm):
    """自定义产品展示表单，支持富文本编辑"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 20,
            'style': 'width: 100%; font-family: monospace;'
        }),
        label='展示内容',
        help_text='支持HTML和Markdown格式，可添加图片和视频'
    )
    
    class Meta:
        model = ProductShow
        fields = '__all__'
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
        }


@admin.register(ProductShowCategory)
class ProductShowCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'shows_count', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order']
    
    def shows_count(self, obj):
        """显示产品展示数量"""
        count = obj.product_shows.filter(status='published').count()
        return format_html('<span style="color: #00a854;">{}</span>', count)
    shows_count.short_description = '展示页数'


@admin.register(ProductShow)
class ProductShowAdmin(admin.ModelAdmin):
    form = ProductShowAdminForm
    list_display = [
        'title_display', 'category', 'game', 'author_name', 'status_display',
        'is_top', 'is_hot', 'is_recommended', 'view_count_display', 
        'published_at', 'created_at'
    ]
    list_filter = [
        'category', 'game', 'status', 'is_top', 'is_hot', 
        'is_recommended', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'author_name']
    list_editable = ['is_top', 'is_hot', 'is_recommended']
    readonly_fields = [
        'view_count', 'like_count', 
        'created_at', 'updated_at', 'preview_link'
    ]
    date_hierarchy = 'published_at'
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'category', 'game', 'author', 'author_name', 'cover_image')
        }),
        ('内容编辑', {
            'fields': ('excerpt', 'content'),
            'classes': ('wide',),
            'description': '支持HTML和Markdown格式编写，可以添加图片、视频等富媒体内容'
        }),
        ('发布设置', {
            'fields': (
                'status', 'is_top', 'is_hot', 'is_recommended', 
                'published_at', 'preview_link'
            ),
        }),
        ('统计信息', {
            'fields': ('view_count', 'like_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_display(self, obj):
        """显示标题和状态标签"""
        title = obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        badges = []
        if obj.is_top:
            badges.append('<span style="background: #f50; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">置顶</span>')
        if obj.is_hot:
            badges.append('<span style="background: #ff5722; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">热门</span>')
        if obj.is_recommended:
            badges.append('<span style="background: #2196f3; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">推荐</span>')
        return format_html('{}{}'.format(title, ''.join(badges)))
    title_display.short_description = '标题'
    
    def status_display(self, obj):
        """显示状态彩色标签"""
        status_colors = {
            'draft': '#999',
            'published': '#52c41a',
            'archived': '#faad14'
        }
        status_text = dict(ProductShow.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            status_colors.get(obj.status, '#999'),
            status_text
        )
    status_display.short_description = '状态'
    
    def view_count_display(self, obj):
        """显示浏览量"""
        return format_html('<strong style="color: #1890ff;">{}</strong>', obj.view_count)
    view_count_display.short_description = '浏览量'
    
    def preview_link(self, obj):
        """预览链接"""
        if obj.pk:
            return format_html(
                '<a href="/product-show/{}" target="_blank" style="color: #1890ff;">预览页面</a>',
                obj.id
            )
        return '-'
    preview_link.short_description = '预览'
    
    def save_model(self, request, obj, form, change):
        """保存模型时的额外处理"""
        if not obj.author_id:
            obj.author = request.user
        
        # 自动生成slug
        if not obj.slug:
            from django.utils.text import slugify
            import uuid
            obj.slug = f"{slugify(obj.title[:50])}-{uuid.uuid4().hex[:8]}"
        
        super().save_model(request, obj, form, change)
