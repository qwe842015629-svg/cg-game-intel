from django.db import models


class ContactMethod(models.Model):
    """联系方式"""
    CONTACT_TYPE_CHOICES = [
        ('online_chat', '在线客服'),
        ('email', '邮件支持'),
        ('phone', '电话客服'),
        ('wechat', '微信客服'),
    ]
    
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, unique=True, verbose_name='联系方式类型')
    title = models.CharField(max_length=100, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    contact_info = models.CharField(max_length=200, verbose_name='联系信息', help_text='如：电话号码、邮箱地址、微信号等')
    icon = models.CharField(max_length=50, default='MessageCircle', verbose_name='图标名称', help_text='Lucide图标名称')
    button_text = models.CharField(max_length=50, verbose_name='按钮文字')
    button_link = models.CharField(max_length=500, blank=True, verbose_name='按钮链接', help_text='留空则不可点击')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '联系方式'
        verbose_name_plural = '联系方式'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.get_contact_type_display()} - {self.title}'


class FAQ(models.Model):
    """常见问题"""
    question = models.CharField(max_length=200, verbose_name='问题')
    answer = models.TextField(verbose_name='回答')
    category = models.CharField(max_length=50, default='general', verbose_name='分类', help_text='如：充值问题、支付问题、账号问题等')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '常见问题'
        verbose_name_plural = '常见问题'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.question


class CustomerServiceConfig(models.Model):
    """客服页面配置"""
    page_title = models.CharField(max_length=100, default='客服中心', verbose_name='页面标题')
    page_description = models.TextField(blank=True, verbose_name='页面描述')
    show_contact_methods = models.BooleanField(default=True, verbose_name='显示联系方式')
    show_faq = models.BooleanField(default=True, verbose_name='显示常见问题')
    faq_title = models.CharField(max_length=100, default='常见问题', verbose_name='常见问题标题')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '客服页面配置'
        verbose_name_plural = '客服页面配置'

    def __str__(self):
        return self.page_title
    
    def save(self, *args, **kwargs):
        # 确保只有一条配置记录
        if not self.pk and CustomerServiceConfig.objects.exists():
            raise ValueError('客服页面配置已存在，请直接修改现有配置')
        return super().save(*args, **kwargs)
