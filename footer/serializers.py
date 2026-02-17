from rest_framework import serializers
from .models import FooterSection, FooterLink, FooterConfig


class FooterLinkSerializer(serializers.ModelSerializer):
    """底部链接序列化器"""
    
    class Meta:
        model = FooterLink
        fields = ['id', 'title', 'url', 'icon', 'is_external', 'is_active', 'sort_order']


class FooterSectionSerializer(serializers.ModelSerializer):
    """页面底部板块序列化器"""
    section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
    links = FooterLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = FooterSection
        fields = ['id', 'section_type', 'section_type_display', 'title', 'description', 
                  'is_active', 'sort_order', 'links', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FooterConfigSerializer(serializers.ModelSerializer):
    """页面底部配置序列化器"""
    
    class Meta:
        model = FooterConfig
        fields = ['id', 'copyright_text', 'show_copyright', 'updated_at']
        read_only_fields = ['updated_at']
