from django.db import models
from django.contrib.auth.models import User
from game_page.models import GamePage


class ArticleCategory(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    name_i18n = models.JSONField(default=dict, blank=True, verbose_name='分类名称多语言')
    description = models.TextField(blank=True, verbose_name='分类描述')
    description_i18n = models.JSONField(default=dict, blank=True, verbose_name='分类描述多语言')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class Article(models.Model):
    """游戏资讯文章"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]

    title = models.CharField(max_length=200, verbose_name='文章标题')
    title_i18n = models.JSONField(default=dict, blank=True, verbose_name='文章标题多语言')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL别名')
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='文章分类'
    )
    game = models.ForeignKey(
        GamePage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name='关联游戏'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='作者'
    )
    author_name = models.CharField(max_length=100, default='游戏小编', verbose_name='作者名称')
    author_name_i18n = models.JSONField(default=dict, blank=True, verbose_name='作者名称多语言')
    tags = models.ManyToManyField('ArticleTag', related_name='articles', blank=True, verbose_name='标签')
    cover_image = models.ImageField(upload_to='articles/', null=True, blank=True, verbose_name='封面图')
    excerpt = models.TextField(max_length=500, blank=True, default='', verbose_name='摘要')
    excerpt_i18n = models.JSONField(default=dict, blank=True, verbose_name='摘要多语言')
    summary = models.TextField(max_length=500, blank=True, default='', verbose_name='摘要')
    summary_i18n = models.JSONField(default=dict, blank=True, verbose_name='摘要补充多语言')
    content = models.TextField(verbose_name='文章内容')
    content_i18n = models.JSONField(default=dict, blank=True, verbose_name='文章内容多语言')
    read_time = models.CharField(max_length=20, default='5分钟', verbose_name='阅读时间')
    read_time_i18n = models.JSONField(default=dict, blank=True, verbose_name='阅读时间多语言')
    
    # SEO优化字段
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='SEO标题')
    meta_description = models.TextField(max_length=300, blank=True, verbose_name='SEO描述')
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name='SEO关键词')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_top = models.BooleanField(default=False, verbose_name='是否置顶')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    comment_count = models.IntegerField(default=0, verbose_name='评论数')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '游戏资讯'
        verbose_name_plural = '游戏资讯'
        ordering = ['-is_top', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def increase_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_tags_list(self):
        """获取标签列表"""
        return list(self.tags.values_list('name', flat=True))


class ArticleTag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    name_i18n = models.JSONField(default=dict, blank=True, verbose_name='标签名称多语言')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '文章标签'
        verbose_name_plural = '文章标签'
        ordering = ['name']

    def __str__(self):
        return self.name


class Comment(models.Model):
    """文章评论"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属文章'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_comments',
        verbose_name='评论用户'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    content = models.TextField(verbose_name='评论内容')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '文章评论'
        verbose_name_plural = '文章评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 在 {self.article.title} 的评论'
