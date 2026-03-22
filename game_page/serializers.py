from rest_framework import serializers

from game_recharge.i18n_utils import localize_text, localize_text_with_variants, resolve_request_locale

from .models import GamePage, GamePageCategory


def _resolve_serializer_locale(context: dict) -> str:
    request = context.get("request") if isinstance(context, dict) else None
    return resolve_request_locale(request)


def _localize_game_field(instance, field_name: str, locale: str, tw_field_name: str | None = None) -> str:
    default_value = getattr(instance, field_name, "")
    i18n_map = getattr(instance, f"{field_name}_i18n", {})

    # Keep historical zh-TW dedicated fields as first fallback.
    if locale == "zh-TW" and tw_field_name:
        return localize_text_with_variants(
            locale,
            (getattr(instance, tw_field_name, ""), {}),
            (default_value, i18n_map),
        )
    return localize_text(default_value, i18n_map, locale)


class GamePageCategorySerializer(serializers.ModelSerializer):
    """游戏页面分类序列化器"""

    game_pages_count = serializers.IntegerField(source="games.count", read_only=True)

    class Meta:
        model = GamePageCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
            "game_pages_count",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["name"] = _localize_game_field(instance, "name", locale)
        data["description"] = _localize_game_field(instance, "description", locale)
        return data


class GamePageListSerializer(serializers.ModelSerializer):
    """游戏页面列表序列化器（简化版）"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    icon_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()

    class Meta:
        model = GamePage
        fields = [
            "id",
            "title",
            "title_tw",
            "slug",
            "category",
            "category_name",
            "developer",
            "platform",
            "regions",
            "icon_external_url",
            "icon_image_url",
            "banner_image_url",
            "description",
            "status",
            "is_hot",
            "is_recommended",
            "sort_order",
            "view_count",
            "like_count",
            "published_at",
            "created_at",
        ]
        read_only_fields = ["view_count", "like_count", "created_at", "updated_at"]

    def get_icon_image_url(self, obj):
        if obj.icon_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
        return None

    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))

        data["title"] = _localize_game_field(instance, "title", locale, tw_field_name="title_tw")
        data["platform"] = _localize_game_field(instance, "platform", locale)
        data["regions"] = _localize_game_field(instance, "regions", locale)
        data["description"] = _localize_game_field(
            instance, "description", locale, tw_field_name="description_tw"
        )

        category = getattr(instance, "category", None)
        data["category_name"] = (
            _localize_game_field(category, "name", locale) if category is not None else ""
        )
        return data


class GamePageDetailSerializer(serializers.ModelSerializer):
    """游戏页面详情序列化器（完整版）"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_info = GamePageCategorySerializer(source="category", read_only=True)
    icon_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()

    class Meta:
        model = GamePage
        fields = [
            "id",
            "title",
            "title_tw",
            "slug",
            "category",
            "category_name",
            "category_info",
            "icon_image",
            "icon_external_url",
            "icon_image_url",
            "banner_image",
            "banner_image_url",
            "developer",
            "platform",
            "regions",
            "server_name",
            "description",
            "description_tw",
            "content",
            "content_tw",
            "topup_info",
            "topup_info_tw",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "status",
            "is_hot",
            "is_recommended",
            "sort_order",
            "view_count",
            "like_count",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["view_count", "like_count", "created_at", "updated_at"]

    def get_icon_image_url(self, obj):
        if obj.icon_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
        return None

    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))

        data["title"] = _localize_game_field(instance, "title", locale, tw_field_name="title_tw")
        data["platform"] = _localize_game_field(instance, "platform", locale)
        data["regions"] = _localize_game_field(instance, "regions", locale)
        data["description"] = _localize_game_field(
            instance, "description", locale, tw_field_name="description_tw"
        )
        data["content"] = _localize_game_field(instance, "content", locale, tw_field_name="content_tw")
        data["topup_info"] = _localize_game_field(
            instance, "topup_info", locale, tw_field_name="topup_info_tw"
        )

        category = getattr(instance, "category", None)
        data["category_name"] = (
            _localize_game_field(category, "name", locale) if category is not None else ""
        )
        return data


class GamePageCreateUpdateSerializer(serializers.ModelSerializer):
    """游戏页面创建/更新序列化器"""

    class Meta:
        model = GamePage
        fields = "__all__"

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
