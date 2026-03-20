from rest_framework import serializers

from .models import DailyRobotConfig, OperationApproval, OperationAuditLog


class CreatePublishRequestSerializer(serializers.Serializer):
    seo_article_id = serializers.IntegerField(min_value=1)
    publish_now = serializers.BooleanField(default=False)
    run_step5 = serializers.BooleanField(default=True)
    publish_at = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="")
    risk_level = serializers.IntegerField(required=False, min_value=1, max_value=5, default=3)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, max_length=100, default="")


class ApprovalDecisionSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")


class ApprovalExecuteSerializer(serializers.Serializer):
    force = serializers.BooleanField(default=False)


class AutomationGooglePlayImportSerializer(serializers.Serializer):
    play_urls = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
    )
    package_ids = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        allow_empty=True,
    )
    template_key = serializers.CharField(required=False, allow_blank=True, max_length=50, default="default")
    category_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    publish_status = serializers.ChoiceField(required=False, choices=["draft", "published"], default="draft")
    overwrite_existing = serializers.BooleanField(required=False, default=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)


class AutomationSeoDailyRunSerializer(serializers.Serializer):
    game_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
    limit_games = serializers.IntegerField(required=False, min_value=1, max_value=100, default=6)
    posts_min = serializers.IntegerField(required=False, min_value=1, max_value=200, default=10)
    posts_max = serializers.IntegerField(required=False, min_value=1, max_value=200, default=20)
    max_attempts_per_game = serializers.IntegerField(required=False, min_value=1, max_value=5, default=1)
    rewrite_limit = serializers.IntegerField(required=False, min_value=1, max_value=5, default=1)
    publish_status = serializers.ChoiceField(required=False, choices=["draft", "published"])
    publish_now = serializers.BooleanField(required=False, default=True)
    rewrite_low_quality = serializers.BooleanField(required=False, default=True)
    review_threshold = serializers.IntegerField(required=False, min_value=1, max_value=100, default=72)
    recent_days = serializers.IntegerField(required=False, min_value=1, max_value=120, default=30)

    def validate(self, attrs):
        posts_min = int(attrs.get("posts_min") or 10)
        posts_max = int(attrs.get("posts_max") or 20)
        if posts_max < posts_min:
            raise serializers.ValidationError({"posts_max": "`posts_max` must be >= `posts_min`."})
        publish_status_raw = attrs.get("publish_status")
        publish_status = str(publish_status_raw or "").strip().lower()
        if publish_status not in {"draft", "published"}:
            publish_status = "published" if bool(attrs.get("publish_now", True)) else "draft"
        attrs["publish_status"] = publish_status
        attrs["publish_now"] = publish_status == "published"
        return attrs


class AutomationPublishedReviewSerializer(serializers.Serializer):
    game_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
    limit = serializers.IntegerField(required=False, min_value=1, max_value=300, default=100)
    rewrite_low_quality = serializers.BooleanField(required=False, default=True)
    archive_duplicates = serializers.BooleanField(required=False, default=True)
    review_threshold = serializers.IntegerField(required=False, min_value=1, max_value=100, default=72)


class DailyRobotConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRobotConfig
        fields = [
            "id",
            "config_key",
            "is_enabled",
            "daily_hour",
            "poll_seconds",
            "max_running_minutes",
            "import_limit",
            "limit_games",
            "posts_min",
            "posts_max",
            "max_attempts_per_game",
            "rewrite_limit",
            "review_threshold",
            "recent_days",
            "publish_status",
            "publish_now",
            "actor_username",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "config_key", "updated_by", "created_at", "updated_at"]

    def validate(self, attrs):
        merged = {
            "daily_hour": int(attrs.get("daily_hour", getattr(self.instance, "daily_hour", 4))),
            "poll_seconds": int(attrs.get("poll_seconds", getattr(self.instance, "poll_seconds", 900))),
            "max_running_minutes": int(
                attrs.get("max_running_minutes", getattr(self.instance, "max_running_minutes", 180))
            ),
            "import_limit": int(attrs.get("import_limit", getattr(self.instance, "import_limit", 30))),
            "limit_games": int(attrs.get("limit_games", getattr(self.instance, "limit_games", 6))),
            "posts_min": int(attrs.get("posts_min", getattr(self.instance, "posts_min", 10))),
            "posts_max": int(attrs.get("posts_max", getattr(self.instance, "posts_max", 20))),
            "max_attempts_per_game": int(
                attrs.get("max_attempts_per_game", getattr(self.instance, "max_attempts_per_game", 1))
            ),
            "rewrite_limit": int(attrs.get("rewrite_limit", getattr(self.instance, "rewrite_limit", 1))),
            "review_threshold": int(
                attrs.get("review_threshold", getattr(self.instance, "review_threshold", 78))
            ),
            "recent_days": int(attrs.get("recent_days", getattr(self.instance, "recent_days", 30))),
            "publish_status": str(
                attrs.get("publish_status", getattr(self.instance, "publish_status", "published")) or "published"
            ).strip().lower(),
        }

        if merged["daily_hour"] < 0 or merged["daily_hour"] > 23:
            raise serializers.ValidationError({"daily_hour": "daily_hour must be between 0 and 23."})
        if merged["poll_seconds"] < 60 or merged["poll_seconds"] > 86400:
            raise serializers.ValidationError({"poll_seconds": "poll_seconds must be between 60 and 86400."})
        if merged["max_running_minutes"] < 10 or merged["max_running_minutes"] > 1440:
            raise serializers.ValidationError(
                {"max_running_minutes": "max_running_minutes must be between 10 and 1440."}
            )
        if merged["import_limit"] < 1 or merged["import_limit"] > 100:
            raise serializers.ValidationError({"import_limit": "import_limit must be between 1 and 100."})
        if merged["limit_games"] < 1 or merged["limit_games"] > 100:
            raise serializers.ValidationError({"limit_games": "limit_games must be between 1 and 100."})
        if merged["posts_min"] < 1 or merged["posts_min"] > 200:
            raise serializers.ValidationError({"posts_min": "posts_min must be between 1 and 200."})
        if merged["posts_max"] < merged["posts_min"] or merged["posts_max"] > 200:
            raise serializers.ValidationError(
                {"posts_max": "posts_max must be >= posts_min and <= 200."}
            )
        if merged["max_attempts_per_game"] < 1 or merged["max_attempts_per_game"] > 5:
            raise serializers.ValidationError(
                {"max_attempts_per_game": "max_attempts_per_game must be between 1 and 5."}
            )
        if merged["rewrite_limit"] < 1 or merged["rewrite_limit"] > 5:
            raise serializers.ValidationError({"rewrite_limit": "rewrite_limit must be between 1 and 5."})
        if merged["review_threshold"] < 1 or merged["review_threshold"] > 100:
            raise serializers.ValidationError({"review_threshold": "review_threshold must be between 1 and 100."})
        if merged["recent_days"] < 1 or merged["recent_days"] > 120:
            raise serializers.ValidationError({"recent_days": "recent_days must be between 1 and 120."})
        if merged["publish_status"] not in {"draft", "published"}:
            raise serializers.ValidationError({"publish_status": "publish_status must be draft or published."})

        if "publish_status" in attrs:
            attrs["publish_now"] = merged["publish_status"] == "published"
        elif "publish_now" in attrs:
            attrs["publish_status"] = "published" if bool(attrs.get("publish_now")) else "draft"

        return attrs


class OperationApprovalSerializer(serializers.ModelSerializer):
    requested_by_username = serializers.CharField(source="requested_by.username", read_only=True)
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)
    executed_by_username = serializers.CharField(source="executed_by.username", read_only=True)

    class Meta:
        model = OperationApproval
        fields = [
            "request_id",
            "action",
            "target_type",
            "target_id",
            "payload",
            "status",
            "risk_level",
            "reason",
            "idempotency_key",
            "client_id",
            "client_ip",
            "requested_by",
            "requested_by_username",
            "approved_by",
            "approved_by_username",
            "executed_by",
            "executed_by_username",
            "requested_at",
            "approved_at",
            "executed_at",
            "failed_at",
            "updated_at",
            "error_message",
            "last_result",
        ]
        read_only_fields = fields


class OperationAuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = OperationAuditLog
        fields = [
            "id",
            "approval",
            "event_type",
            "actor",
            "actor_username",
            "actor_name",
            "client_id",
            "client_ip",
            "request_snapshot",
            "result_snapshot",
            "message",
            "created_at",
        ]
        read_only_fields = fields
