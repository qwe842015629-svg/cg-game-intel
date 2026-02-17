from rest_framework import serializers
from .models import GameCategory, Game, ProductType, Product


class GameCategorySerializer(serializers.ModelSerializer):
    """游戏分类序列化器"""
    games_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GameCategory
        fields = ['id', 'name', 'code', 'icon', 'icon_image', 'sort_order', 'is_active', 'games_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_games_count(self, obj):
        """获取该分类下的游戏数量"""
        return obj.games.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """充值商品序列化器（用于游戏详情中的rechargeOptions）"""
    class Meta:
        model = Product
        fields = ['id', 'amount', 'current_price', 'original_price', 'discount', 'is_popular']
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        return {
            'id': str(instance.id),
            'amount': instance.amount,
            'price': float(instance.current_price),
            'originalPrice': float(instance.original_price) if instance.original_price else None,
            'discount': instance.discount if instance.discount > 0 else None,
            'popular': instance.is_popular,
        }


class GameListSerializer(serializers.ModelSerializer):
    """游戏列表序列化器（简化版，用于列表和卡片展示）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = ['id', 'name', 'name_en', 'icon', 'cover', 'description', 'category_code', 
                  'category_name', 'is_hot', 'tags', 'processing_time']
    
    def get_tags(self, obj):
        """获取标签列表"""
        return obj.get_tags_list()
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        return {
            'id': str(instance.id),
            'name': instance.name,
            'nameEn': instance.name_en,
            'image': instance.cover.url if instance.cover else (instance.icon.url if instance.icon else ''),
            'category': instance.category.code if instance.category else 'international',
            'categoryName': instance.category.name if instance.category else '国际游戏',
            'hot': instance.is_hot,
            'tags': self.get_tags(instance),
            'description': instance.description,
            'processingTime': instance.processing_time,
        }


class GameDetailSerializer(serializers.ModelSerializer):
    """游戏详情序列化器（完整版，包含充值选项）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    tags = serializers.SerializerMethodField()
    payment_methods = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    instructions = serializers.SerializerMethodField()
    recharge_options = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = ['id', 'name', 'name_en', 'icon', 'cover', 'description', 'category_code',
                  'category_name', 'is_hot', 'tags', 'payment_methods', 'recharge_options',
                  'instructions', 'processing_time', 'region']
    
    def get_tags(self, obj):
        return obj.get_tags_list()
    
    def get_payment_methods(self, obj):
        return obj.get_payment_methods_list()
    
    def get_region(self, obj):
        return obj.get_regions_list()
    
    def get_instructions(self, obj):
        return obj.get_instructions_list()
    
    def get_recharge_options(self, obj):
        """获取充值选项列表"""
        products = obj.products.filter(is_active=True).order_by('sort_order', 'current_price')
        return ProductSerializer(products, many=True).data
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        return {
            'id': str(instance.id),
            'name': instance.name,
            'nameEn': instance.name_en,
            'image': instance.cover.url if instance.cover else (instance.icon.url if instance.icon else ''),
            'category': instance.category.code if instance.category else 'international',
            'categoryName': instance.category.name if instance.category else '国际游戏',
            'hot': instance.is_hot,
            'tags': self.get_tags(instance),
            'description': instance.description,
            'paymentMethods': self.get_payment_methods(instance),
            'rechargeOptions': self.get_recharge_options(instance),
            'instructions': self.get_instructions(instance),
            'processingTime': instance.processing_time,
            'region': self.get_region(instance),
        }


class ProductTypeSerializer(serializers.ModelSerializer):
    """商品类型序列化器"""
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'code', 'description', 'created_at']
        read_only_fields = ['created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """商品列表序列化器（简化版）"""
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_icon = serializers.ImageField(source='game.icon', read_only=True)
    type_name = serializers.CharField(source='product_type.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'game', 'game_name', 'game_icon', 'product_type', 'type_name', 
                  'name', 'current_price', 'original_price', 'discount', 'product_image',
                  'is_hot', 'is_recommended', 'sales_count']


class ProductDetailSerializer(serializers.ModelSerializer):
    """商品详情序列化器（完整版）"""
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_icon = serializers.ImageField(source='game.icon', read_only=True)
    type_name = serializers.CharField(source='product_type.name', read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'game', 'game_name', 'game_icon', 'product_type', 'type_name',
                  'name', 'description', 'current_price', 'original_price', 'discount',
                  'stock', 'is_in_stock', 'sales_count', 'product_image',
                  'is_hot', 'is_recommended', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['discount', 'sales_count', 'created_at', 'updated_at']
