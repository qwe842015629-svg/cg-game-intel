from django.db import models
from django.contrib.auth.models import User
from game_product.models import Game


class ProductShowCategory(models.Model):
    """游戏产品展示分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '产品展示分类'
        verbose_name_plural = '产品展示分类'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class ProductShow(models.Model):
    """游戏产品展示页"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]

    title = models.CharField(max_length=200, verbose_name='展示标题')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL别名')
    category = models.ForeignKey(
        ProductShowCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product_shows',
        verbose_name='展示分类'
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_shows',
        verbose_name='关联游戏'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product_shows',
        verbose_name='作者'
    )
    author_name = models.CharField(max_length=100, default='产品运营', verbose_name='作者名称')
    
    # 封面图和主图
    cover_image = models.ImageField(upload_to='product_shows/', null=True, blank=True, verbose_name='封面图')
    
    # 内容字段
    excerpt = models.TextField(max_length=500, blank=True, default='', verbose_name='摘要')
    content = models.TextField(verbose_name='展示内容')
    
    # 状态和展示设置
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_top = models.BooleanField(default=False, verbose_name='是否置顶')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    
    # 统计字段
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    
    # 时间字段
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '游戏产品展示'
        verbose_name_plural = '游戏产品展示'
        ordering = ['-is_top', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def increase_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
