from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django import forms
from .models import ArticleCategory, Article, ArticleTag, Comment


class ArticleAdminForm(forms.ModelForm):
    """自定义文章表单，支持富文本编辑"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 20,
            'style': 'width: 100%; font-family: monospace;'
        }),
        label='文章内容',
        help_text='支持Markdown格式和HTML'
    )
    
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}),
            'meta_description': forms.Textarea(attrs={'rows': 2, 'style': 'width: 100%;'}),
        }


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'articles_count', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order']
    
    def articles_count(self, obj):
        """显示文章数量"""
        count = obj.articles.filter(status='published').count()
        return format_html('<span style="color: #00a854;">{}</span>', count)
    articles_count.short_description = '文章数'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = [
        'title_display', 'category', 'game', 'author_name', 'status_display',
        'is_top', 'is_hot', 'is_recommended', 'view_count_display', 
        'published_at', 'created_at'
    ]
    list_filter = [
        'category', 'game', 'status', 'is_top', 'is_hot', 
        'is_recommended', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'author_name', 'meta_keywords']
    list_editable = ['is_top', 'is_hot', 'is_recommended']
    readonly_fields = [
        'view_count', 'like_count', 'comment_count', 
        'created_at', 'updated_at', 'preview_link'
    ]
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'category', 'game', 'author', 'author_name', 'cover_image')
        }),
        ('内容编辑', {
            'fields': ('excerpt', 'summary', 'content', 'read_time'),
            'classes': ('wide',),
            'description': '使用Markdown或HTML格式编写文章内容'
        }),
        ('SEO优化', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': '搜索引擎优化设置，建议填写'
        }),
        ('标签与分类', {
            'fields': ('tags',),
        }),
        ('发布设置', {
            'fields': (
                'status', 'is_top', 'is_hot', 'is_recommended', 
                'published_at', 'preview_link'
            ),
        }),
        ('统计信息', {
            'fields': ('view_count', 'like_count', 'comment_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_display(self, obj):
        """显示文章标题和状态标签"""
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
        status_text = dict(Article.STATUS_CHOICES).get(obj.status, obj.status)
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
                '<a href="/articles/{}" target="_blank" style="color: #1890ff;">预览文章</a>',
                obj.id
            )
        return '-'
    preview_link.short_description = '预览'
    
    def save_model(self, request, obj, form, change):
        """保存模型时的额外处理"""
        if not obj.author_id:
            obj.author = request.user
        
        # 如果没有设置SEO标题，使用文章标题
        if not obj.meta_title:
            obj.meta_title = obj.title
        
        # 如果没有设置SEO描述，使用摘要
        if not obj.meta_description and obj.excerpt:
            obj.meta_description = obj.excerpt[:300]
        
        # 自动生成slug
        if not obj.slug:
            from django.utils.text import slugify
            import uuid
            obj.slug = f"{slugify(obj.title[:50])}-{uuid.uuid4().hex[:8]}"
        
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/article_admin.css', 'admin/css/media_picker.css')
        }
        js = ('admin/js/article_admin.js', 'admin/js/media_picker_widget.js')


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'articles_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def articles_count(self, obj):
        """显示使用该标签的文章数"""
        count = obj.articles.filter(status='published').count()
        return format_html('<span style="color: #00a854;">{}</span>', count)
    articles_count.short_description = '文章数'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'article_title', 'user_name', 'content_preview', 
        'parent_preview', 'is_approved', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'user__username', 'article__title']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    raw_id_fields = ['article', 'user', 'parent']
    list_per_page = 50
    
    def article_title(self, obj):
        """显示文章标题"""
        return obj.article.title[:30] + '...' if len(obj.article.title) > 30 else obj.article.title
    article_title.short_description = '文章'
    
    def user_name(self, obj):
        """显示用户名"""
        return format_html('<strong>{}</strong>', obj.user.username)
    user_name.short_description = '用户'
    
    def content_preview(self, obj):
        """评论内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'
    
    def parent_preview(self, obj):
        """父评论预览"""
        if obj.parent:
            return obj.parent.content[:30] + '...'
        return '-'
    parent_preview.short_description = '回复评论'
