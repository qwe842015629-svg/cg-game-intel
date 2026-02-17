from rest_framework import serializers

from .models import CrawlerTask, LLMApiSetting, SeoArticle, SeoKeywordWeight


class CrawlerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerTask
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class SeoKeywordWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoKeywordWeight
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class SeoArticleSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source="game.title", read_only=True)
    task_keyword = serializers.CharField(source="task.keyword", read_only=True)

    class Meta:
        model = SeoArticle
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "slug", "game_title", "task_keyword"]


class SeoRewriteRequestSerializer(serializers.Serializer):
    raw_text = serializers.CharField()
    game_name = serializers.CharField(max_length=200)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
    )
    source_title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    source_url = serializers.URLField(required=False, allow_blank=True)
    related_game_id = serializers.IntegerField(required=False, allow_null=True)
    task_id = serializers.IntegerField(required=False, allow_null=True)
    store_draft = serializers.BooleanField(required=False, default=True)


class SeoRewriteResponseSerializer(serializers.Serializer):
    title = serializers.CharField()
    body_html = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    meta_description = serializers.CharField()
    meta_title = serializers.CharField()
    diagnostics = serializers.DictField()
    draft_id = serializers.IntegerField(required=False)


class BahamutTaskRunSerializer(serializers.Serializer):
    source_url = serializers.CharField(required=False, allow_blank=True)
    bsn = serializers.IntegerField(required=False)
    keyword = serializers.CharField(max_length=120, required=False, allow_blank=True)
    start_page = serializers.IntegerField(required=False, default=1, min_value=1)
    end_page = serializers.IntegerField(required=False, default=1, min_value=1)
    max_posts = serializers.IntegerField(required=False, default=20, min_value=1, max_value=200)
    stop_after_step = serializers.IntegerField(required=False, default=5, min_value=1, max_value=5)
    run_rewrite = serializers.BooleanField(required=False, default=True)
    rewrite_limit = serializers.IntegerField(required=False, default=3, min_value=1, max_value=20)
    store_draft = serializers.BooleanField(required=False, default=True)
    auto_publish = serializers.BooleanField(required=False, default=False)
    publish_now = serializers.BooleanField(required=False, default=False)
    publish_at = serializers.CharField(required=False, allow_blank=True)
    related_game_id = serializers.IntegerField(required=False, allow_null=True)
    custom_keywords = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs):
        source_url = (attrs.get("source_url") or "").strip()
        bsn = attrs.get("bsn")
        start_page = attrs.get("start_page", 1)
        end_page = attrs.get("end_page", 1)

        if not source_url and not bsn:
            raise serializers.ValidationError("`source_url` 和 `bsn` 至少提供一个。")
        if end_page < start_page:
            raise serializers.ValidationError("`end_page` 必须大于或等于 `start_page`。")
        return attrs


class LLMApiConnectionTestSerializer(serializers.Serializer):
    base_url = serializers.CharField(max_length=255, required=False, allow_blank=True)
    api_key = serializers.CharField(max_length=255, required=False, allow_blank=True)
    model_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    timeout_seconds = serializers.IntegerField(required=False, min_value=5, max_value=180)

    def validate(self, attrs):
        setting = LLMApiSetting.get_solo()

        base_url = str(attrs.get("base_url") or setting.base_url or "").strip()
        api_key = str(attrs.get("api_key") or setting.api_key or "").strip()
        model_name = str(attrs.get("model_name") or setting.model_name or "grok-4-fast").strip()
        timeout_seconds = attrs.get("timeout_seconds")
        if timeout_seconds is None:
            timeout_seconds = int(setting.timeout_seconds or 45)

        if not base_url:
            raise serializers.ValidationError({"base_url": "Base URL 不能为空"})
        if not api_key:
            raise serializers.ValidationError({"api_key": "API Key 不能为空"})
        if not model_name:
            raise serializers.ValidationError({"model_name": "模型名不能为空"})

        attrs["base_url"] = base_url
        attrs["api_key"] = api_key
        attrs["model_name"] = model_name
        attrs["timeout_seconds"] = timeout_seconds
        return attrs


class LLMApiSettingSerializer(serializers.ModelSerializer):
    model_options = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LLMApiSetting
        fields = [
            "id",
            "name",
            "base_url",
            "api_key",
            "model_name",
            "timeout_seconds",
            "is_active",
            "model_options",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "model_options", "created_at", "updated_at"]

    def get_model_options(self, obj):
        return ["grok-4-fast-reasoning", "grok-4-fast", "grok-4"]
