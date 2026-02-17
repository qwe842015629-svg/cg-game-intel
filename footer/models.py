from django.db import models


class FooterSection(models.Model):
    """页面底部板块"""
    SECTION_TYPE_CHOICES = [
        ('about', '关于我们'),
        ('service', '客服服务'),
        ('payment', '支付方式'),
        ('social', '关注我们'),
    ]
    
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, unique=True, verbose_name='板块类型')
    title = models.CharField(max_length=100, verbose_name='板块标题')
    description = models.TextField(blank=True, verbose_name='描述内容', help_text='适用于"关于我们"等需要描述的板块')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '页面底部板块'
        verbose_name_plural = '页面底部板块'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.get_section_type_display()} - {self.title}'


class FooterLink(models.Model):
    """页面底部链接"""
    section = models.ForeignKey(
        FooterSection,
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='所属板块'
    )
    title = models.CharField(max_length=100, verbose_name='链接标题')
    url = models.CharField(max_length=500, verbose_name='链接地址', help_text='可以是相对路径如/articles，或外部链接如https://twitter.com')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标', help_text='图标类名或Emoji')
    is_external = models.BooleanField(default=False, verbose_name='是否外部链接', help_text='外部链接会在新窗口打开')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '底部链接'
        verbose_name_plural = '底部链接'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.section.title} - {self.title}'


class FooterConfig(models.Model):
    """页面底部配置"""
    copyright_text = models.CharField(max_length=200, default='© 2026 CYPHER GAME BUY. 版权所有', verbose_name='版权信息')
    show_copyright = models.BooleanField(default=True, verbose_name='显示版权信息')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '页面底部配置'
        verbose_name_plural = '页面底部配置'

    def __str__(self):
        return '页面底部配置'
    
    def save(self, *args, **kwargs):
        # 确保只有一条配置记录
        if not self.pk and FooterConfig.objects.exists():
            raise ValueError('页面底部配置已存在，请直接修改现有配置')
        return super().save(*args, **kwargs)
