from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class GamePageCategory(models.Model):
    """游戏分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name='分类别名')
    description = models.TextField(blank=True, verbose_name='分类描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '游戏分类'
        verbose_name_plural = '游戏分类'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GamePage(models.Model):
    """游戏聚合页 (Game Page)"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]

    # 1. 基础信息
    title = models.CharField(max_length=200, verbose_name='游戏名称')
    title_tw = models.CharField(max_length=200, blank=True, verbose_name='游戏名称(繁体)')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL别名')
    category = models.ForeignKey(
        GamePageCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='games',
        verbose_name='游戏分类'
    )
    
    # 2. 视觉素材 (接入素材库)
    icon_image = models.ImageField(upload_to='games/icons/', null=True, blank=True, verbose_name='游戏图标')
    icon_external_url = models.URLField(blank=True, verbose_name='图标外链URL')
    banner_image = models.ImageField(upload_to='games/banners/', null=True, blank=True, verbose_name='Banner大图')
    
    # 3. 游戏特性/参数
    developer = models.CharField(max_length=100, blank=True, verbose_name='开发商')
    platform = models.CharField(max_length=100, default='Android / iOS', verbose_name='支持平台')
    regions = models.CharField(max_length=200, blank=True, default='港台服', verbose_name='支持区服')
    server_name = models.CharField(max_length=100, blank=True, verbose_name='服务器')
    google_play_id = models.CharField(max_length=200, blank=True, verbose_name='Google Play ID')
    
    # 4. 富文本内容
    description = models.TextField(blank=True, verbose_name='简短介绍')
    description_tw = models.TextField(blank=True, verbose_name='简短介绍(繁体)')
    
    content = models.TextField(blank=True, verbose_name='游戏详情')
    content_tw = models.TextField(blank=True, verbose_name='游戏详情(繁体)')
    
    topup_info = models.TextField(blank=True, verbose_name='充值说明')
    topup_info_tw = models.TextField(blank=True, verbose_name='充值说明(繁体)')
    
    # 5. SEO 设置
    seo_title = models.CharField(max_length=200, blank=True, verbose_name='SEO标题')
    seo_description = models.CharField(max_length=500, blank=True, verbose_name='SEO描述')
    seo_keywords = models.CharField(max_length=200, blank=True, verbose_name='SEO关键词')
    
    # 6. 状态与统计
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_hot = models.BooleanField(default=False, verbose_name='热门推荐')
    is_recommended = models.BooleanField(default=False, verbose_name='店长推荐')
    
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='发布者')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '游戏页面'
        verbose_name_plural = '游戏页面管理'
        ordering = ['sort_order', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 自动生成 Slug
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{uuid.uuid4().hex[:6]}"
        
        # 自动生成 SEO 信息 (如果为空)
        if not self.seo_title:
            self.seo_title = f"{self.title}代储_充值 - MEME港台游戏工具箱"
        if not self.seo_keywords:
            self.seo_keywords = f"{self.title},{self.title}代储,{self.title}充值,手游代储"
        if not self.seo_description:
            self.seo_description = f"MEME提供{self.title}手游代储服务，安全秒到账。{self.description[:100]}"
            
        super().save(*args, **kwargs)


class GamePageTemplate(models.Model):
    """Reusable template snippets for game page top-up instructions."""

    key = models.CharField(max_length=50, unique=True, default="default", verbose_name="模板键")
    topup_info = models.TextField(blank=True, verbose_name="默认充值说明")
    topup_info_tw = models.TextField(blank=True, verbose_name="默认充值说明(繁体)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "游戏页面模板"
        verbose_name_plural = "游戏页面模板"

    def __str__(self):
        return self.key

