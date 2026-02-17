from rest_framework import serializers
from .models import ProductShowCategory, ProductShow


class ProductShowCategorySerializer(serializers.ModelSerializer):
    """产品展示分类序列化器"""
    shows_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductShowCategory
        fields = ['id', 'name', 'description', 'sort_order', 'is_active', 'shows_count', 'created_at', 'updated_at']
    
    def get_shows_count(self, obj):
        """获取该分类下的已发布展示页数量"""
        return obj.product_shows.filter(status='published').count()


class ProductShowListSerializer(serializers.ModelSerializer):
    """产品展示列表序列化器"""
    category = serializers.CharField(source='category.name', read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductShow
        fields = [
            'id', 'title', 'slug', 'category', 'game_name',
            'excerpt', 'image', 'author_name',
            'is_top', 'is_hot', 'is_recommended',
            'view_count', 'like_count',
            'published_at', 'created_at'
        ]
    
    def get_image(self, obj):
        """获取封面图URL"""
        if obj.cover_image:
            try:
                return obj.cover_image.url
            except (ValueError, AttributeError):
                return ''
        return ''


class ProductShowDetailSerializer(serializers.ModelSerializer):
    """产品展示详情序列化器"""
    category = ProductShowCategorySerializer(read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductShow
        fields = [
            'id', 'title', 'slug', 'category', 'game_name',
            'excerpt', 'content', 'image', 'author_name',
            'is_top', 'is_hot', 'is_recommended',
            'view_count', 'like_count',
            'published_at', 'created_at', 'updated_at'
        ]
    
    def get_image(self, obj):
        """获取封面图URL"""
        if obj.cover_image:
            try:
                return obj.cover_image.url
            except (ValueError, AttributeError):
                return ''
        return ''
