from django.db import models
from django.contrib.auth.models import User


class GameCategory(models.Model):
    """游戏分类"""
    CATEGORY_CHOICES = [
        ('international', '国际游戏'),
        ('hongkong-taiwan', '港台游戏'),
        ('southeast-asia', '东南亚游戏'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='分类名称')
    code = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='international', verbose_name='分类代码')
    icon = models.CharField(max_length=10, default='🎮', verbose_name='分类图标Emoji')
    icon_image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='分类图标图片')
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


class Game(models.Model):
    """游戏信息"""
    name = models.CharField(max_length=200, verbose_name='游戏名称')
    name_en = models.CharField(max_length=200, blank=True, default='', verbose_name='游戏英文名称')
    category = models.ForeignKey(GameCategory, on_delete=models.SET_NULL, null=True, related_name='games', verbose_name='游戏分类')
    icon = models.ImageField(upload_to='games/', verbose_name='游戏图标')
    cover = models.ImageField(upload_to='games/covers/', null=True, blank=True, verbose_name='游戏封面')
    description = models.TextField(blank=True, verbose_name='游戏描述')
    developer = models.CharField(max_length=200, blank=True, verbose_name='开发商')
    tags = models.CharField(max_length=500, blank=True, default='', help_text='用逗号分隔，如：RPG,开放世界,热门', verbose_name='标签')
    regions = models.CharField(max_length=500, blank=True, default='', help_text='用逗号分隔，如：国服,美服,欧服', verbose_name='支持区服')
    payment_methods = models.CharField(max_length=200, default='alipay,wechat', help_text='用逗号分隔', verbose_name='支付方式')
    processing_time = models.CharField(max_length=50, default='1-10分钟', verbose_name='到账时间')
    instructions = models.TextField(blank=True, help_text='充值说明，每行一条', verbose_name='充值说明')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '游戏'
        verbose_name_plural = '游戏'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name
    
    def get_tags_list(self):
        """获取标签列表"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_regions_list(self):
        """获取区服列表"""
        return [region.strip() for region in self.regions.split(',') if region.strip()]
    
    def get_payment_methods_list(self):
        """获取支付方式列表"""
        return [method.strip() for method in self.payment_methods.split(',') if method.strip()]
    
    def get_instructions_list(self):
        """获取充值说明列表"""
        return [line.strip() for line in self.instructions.split('\n') if line.strip()]


class ProductType(models.Model):
    """商品类型"""
    POINT = 'point'  # 点券/点卡
    VIP = 'vip'  # 会员
    ITEM = 'item'  # 道具
    GIFT = 'gift'  # 礼包
    OTHER = 'other'  # 其他

    TYPE_CHOICES = [
        (POINT, '点券/点卡'),
        (VIP, '会员'),
        (ITEM, '道具'),
        (GIFT, '礼包'),
        (OTHER, '其他'),
    ]

    name = models.CharField(max_length=50, verbose_name='类型名称')
    code = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True, verbose_name='类型代码')
    description = models.TextField(blank=True, verbose_name='类型描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品类型'
        verbose_name_plural = '商品类型'

    def __str__(self):
        return self.name


class Product(models.Model):
    """充值商品"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='products', verbose_name='所属游戏')
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='商品类型')
    name = models.CharField(max_length=200, verbose_name='商品名称')
    amount = models.CharField(max_length=100, default='', verbose_name='充值数量', help_text='如：60创世结晶、300点券')
    description = models.TextField(blank=True, verbose_name='商品描述')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='现价')
    discount = models.IntegerField(default=0, verbose_name='折扣（百分比）', help_text='0表示无折扣')
    is_popular = models.BooleanField(default=False, verbose_name='是否推荐')
    stock = models.IntegerField(default=9999, verbose_name='库存')
    sales_count = models.IntegerField(default=0, verbose_name='销量')
    product_image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='商品图片')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '充值商品'
        verbose_name_plural = '充值商品'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f'{self.game.name} - {self.name}'

    @property
    def is_in_stock(self):
        """是否有库存"""
        return self.stock > 0

    def save(self, *args, **kwargs):
        # 自动计算折扣
        if self.original_price and self.original_price > 0:
            self.discount = int((1 - float(self.current_price) / float(self.original_price)) * 100)
        super().save(*args, **kwargs)
