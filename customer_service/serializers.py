from rest_framework import serializers
from .models import ContactMethod, FAQ, CustomerServiceConfig


class ContactMethodSerializer(serializers.ModelSerializer):
    """联系方式序列化器"""
    contact_type_display = serializers.CharField(source='get_contact_type_display', read_only=True)
    
    class Meta:
        model = ContactMethod
        fields = ['id', 'contact_type', 'contact_type_display', 'title', 'description', 
                  'contact_info', 'icon', 'button_text', 'button_link', 'is_active', 
                  'sort_order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FAQSerializer(serializers.ModelSerializer):
    """常见问题序列化器"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'is_active', 
                  'sort_order', 'view_count', 'created_at', 'updated_at']
        read_only_fields = ['view_count', 'created_at', 'updated_at']


class CustomerServiceConfigSerializer(serializers.ModelSerializer):
    """客服页面配置序列化器"""
    
    class Meta:
        model = CustomerServiceConfig
        fields = ['id', 'page_title', 'page_description', 'show_contact_methods', 
                  'show_faq', 'faq_title', 'updated_at']
        read_only_fields = ['updated_at']
