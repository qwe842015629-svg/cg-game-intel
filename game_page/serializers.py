from rest_framework import serializers
from .models import GamePage, GamePageCategory


class GamePageCategorySerializer(serializers.ModelSerializer):
    """游戏页面分类序列化器"""
    game_pages_count = serializers.IntegerField(source='games.count', read_only=True)
    
    class Meta:
        model = GamePageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'sort_order', 
            'is_active', 'created_at', 'updated_at', 'game_pages_count'
        ]
        read_only_fields = ['created_at', 'updated_at']


class GamePageListSerializer(serializers.ModelSerializer):
    """游戏页面列表序列化器（简化版）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    icon_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GamePage
        fields = [
            'id', 'title', 'title_tw', 'slug', 'category', 'category_name',
            'developer', 'platform', 'regions',
            'icon_external_url', 'icon_image_url', 'banner_image_url',
            'description', 'status', 'is_hot', 'is_recommended', 'sort_order',
            'view_count', 'like_count', 'published_at', 'created_at'
        ]
        read_only_fields = ['view_count', 'like_count', 'created_at', 'updated_at']
    
    def get_icon_image_url(self, obj):
        if obj.icon_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
        return None

    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
        return None


class GamePageDetailSerializer(serializers.ModelSerializer):
    """游戏页面详情序列化器（完整版）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_info = GamePageCategorySerializer(source='category', read_only=True)
    icon_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GamePage
        fields = [
            'id', 'title', 'title_tw', 'slug', 'category', 'category_name', 'category_info',
            'icon_image', 'icon_external_url', 'icon_image_url', 'banner_image', 'banner_image_url',
            'developer', 'platform', 'regions', 'server_name',
            'description', 'description_tw',
            'content', 'content_tw',
            'topup_info', 'topup_info_tw',
            'seo_title', 'seo_description', 'seo_keywords',
            'status', 'is_hot', 'is_recommended', 'sort_order',
            'view_count', 'like_count', 'author', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['view_count', 'like_count', 'created_at', 'updated_at']
    
    def get_icon_image_url(self, obj):
        if obj.icon_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
        return None

    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
        return None


class GamePageCreateUpdateSerializer(serializers.ModelSerializer):
    """游戏页面创建/更新序列化器"""
    
    class Meta:
        model = GamePage
        fields = '__all__'
    
    def validate_slug(self, value):
        """验证 slug 唯一性"""
        instance = self.instance
        if value:
            qs = GamePage.objects.filter(slug=value)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError("该 URL 别名已存在")
        return value
