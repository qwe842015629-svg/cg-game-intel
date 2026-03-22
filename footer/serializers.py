from rest_framework import serializers

from game_recharge.i18n_utils import localize_text, resolve_request_locale

from .models import FooterSection, FooterLink, FooterConfig


def _resolve_serializer_locale(context: dict) -> str:
    request = context.get("request") if isinstance(context, dict) else None
    return resolve_request_locale(request)


class FooterLinkSerializer(serializers.ModelSerializer):
    """底部链接序列化器"""
    
    class Meta:
        model = FooterLink
        fields = ['id', 'title', 'url', 'icon', 'is_external', 'is_active', 'sort_order']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["title"] = localize_text(instance.title, getattr(instance, "title_i18n", {}), locale)
        return data


class FooterSectionSerializer(serializers.ModelSerializer):
    """页面底部板块序列化器"""
    section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
    links = FooterLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = FooterSection
        fields = ['id', 'section_type', 'section_type_display', 'title', 'description', 
                  'is_active', 'sort_order', 'links', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["title"] = localize_text(instance.title, getattr(instance, "title_i18n", {}), locale)
        data["description"] = localize_text(
            instance.description, getattr(instance, "description_i18n", {}), locale
        )
        return data


class FooterConfigSerializer(serializers.ModelSerializer):
    """页面底部配置序列化器"""
    
    class Meta:
        model = FooterConfig
        fields = ['id', 'copyright_text', 'show_copyright', 'updated_at']
        read_only_fields = ['updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["copyright_text"] = localize_text(
            instance.copyright_text, getattr(instance, "copyright_text_i18n", {}), locale
        )
        return data
