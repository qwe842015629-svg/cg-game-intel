from rest_framework import serializers
from .models import Banner, HomeLayout, SiteConfig, MediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    """媒体资源序列化器"""
    url = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField()
    file = serializers.ImageField(write_only=True)

    class Meta:
        model = MediaAsset
        fields = ['id', 'name', 'file', 'url', 'thumbnail_url', 'category', 'alt_text', 'file_size', 'content_hash', 'created_at']
        read_only_fields = ['file_size', 'content_hash', 'created_at']



class SiteConfigSerializer(serializers.ModelSerializer):
    """网站全局配置序列化器"""
    
    class Meta:
        model = SiteConfig
        fields = [
            'site_name', 'site_logo', 'favicon', 
            'seo_keywords', 'seo_description',
            'primary_color', 'secondary_color',
            'contact_email', 'contact_phone',
            'is_maintenance_mode'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 转换为驼峰命名并处理文件路径
        return {
            'siteName': instance.site_name,
            'siteLogo': instance.site_logo.url if instance.site_logo else '',
            'favicon': instance.favicon.url if instance.favicon else '',
            'seoKeywords': instance.seo_keywords,
            'seoDescription': instance.seo_description,
            'primaryColor': instance.primary_color,
            'secondaryColor': instance.secondary_color,
            'contactEmail': instance.contact_email,
            'contactPhone': instance.contact_phone,
            'isMaintenanceMode': instance.is_maintenance_mode,
        }


class BannerSerializer(serializers.ModelSerializer):
    """轮播图序列化器"""
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'description', 'badge', 'image',
            'primary_button_text', 'primary_button_link',
            'secondary_button_text', 'secondary_button_link',
            'sort_order', 'view_count', 'click_count'
        ]
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        # 增加查看次数
        instance.increase_view_count()
        
        return {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'badge': instance.badge,
            'image': instance.image.url if instance.image else '',
            'primaryButton': instance.primary_button_text,
            'secondaryButton': instance.secondary_button_text,
            'primaryLink': instance.primary_button_link,
            'secondaryLink': instance.secondary_button_link,
        }


class BannerListSerializer(serializers.ModelSerializer):
    """轮播图列表序列化器（简化版）"""
    
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'badge', 'sort_order']
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        return {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'badge': instance.badge,
            'image': instance.image.url if instance.image else '',
            'primaryButton': instance.primary_button_text,
            'secondaryButton': instance.secondary_button_text,
            'primaryLink': instance.primary_button_link,
            'secondaryLink': instance.secondary_button_link,
        }


class HomeLayoutSerializer(serializers.ModelSerializer):
    """首页布局序列化器"""
    
    class Meta:
        model = HomeLayout
        fields = [
            'id', 'section_key', 'section_name', 'is_enabled',
            'sort_order', 'config', 'view_count'
        ]
    
    def to_representation(self, instance):
        """转换为前端所需的格式"""
        return {
            'id': instance.id,
            'sectionKey': instance.section_key,
            'section_key': instance.section_key, # 保留原始 Key 用于 API 查询
            'sectionName': instance.section_name,
            'isEnabled': instance.is_enabled,
            'sortOrder': instance.sort_order,
            'config': instance.config or {},
            'viewCount': instance.view_count,
        }
