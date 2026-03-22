from django.contrib import admin

from .models import (
    BahamutBoardRankingEntry,
    BahamutBoardRankingSnapshot,
    DailyRobotConfig,
    DailyRobotRun,
    OperationApproval,
    OperationAuditLog,
)


@admin.register(OperationApproval)
class OperationApprovalAdmin(admin.ModelAdmin):
    list_display = [
        "request_id",
        "action",
        "target_type",
        "target_id",
        "status",
        "risk_level",
        "requested_by",
        "approved_by",
        "executed_by",
        "requested_at",
    ]
    list_filter = ["action", "status", "risk_level", "requested_at", "approved_at", "executed_at"]
    search_fields = ["request_id", "target_id", "idempotency_key", "reason", "error_message", "client_id", "client_ip"]
    readonly_fields = [
        "request_id",
        "requested_at",
        "approved_at",
        "executed_at",
        "failed_at",
        "updated_at",
    ]
    ordering = ["-requested_at"]


@admin.register(OperationAuditLog)
class OperationAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "approval",
        "event_type",
        "actor",
        "client_id",
        "client_ip",
        "created_at",
    ]
    list_filter = ["event_type", "created_at"]
    search_fields = ["approval__request_id", "message", "actor_name", "client_id", "client_ip"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]


@admin.register(DailyRobotRun)
class DailyRobotRunAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "run_key",
        "run_date",
        "trigger_source",
        "status",
        "started_at",
        "finished_at",
    ]
    list_filter = ["run_key", "status", "trigger_source", "run_date"]
    search_fields = ["run_key", "error_message"]
    readonly_fields = ["started_at", "finished_at", "updated_at"]
    ordering = ["-run_date", "-started_at", "-id"]


@admin.register(DailyRobotConfig)
class DailyRobotConfigAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "config_key",
        "is_enabled",
        "daily_hour",
        "publish_status",
        "import_limit",
        "limit_games",
        "posts_min",
        "posts_max",
        "max_attempts_per_game",
        "rewrite_limit",
        "review_threshold",
        "updated_at",
    ]
    list_filter = ["is_enabled", "publish_status", "daily_hour", "updated_at"]
    search_fields = ["config_key", "actor_username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(BahamutBoardRankingSnapshot)
class BahamutBoardRankingSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "snapshot_date",
        "trigger_source",
        "status",
        "total_raw_count",
        "game_count",
        "started_at",
        "finished_at",
    ]
    list_filter = ["status", "trigger_source", "snapshot_date"]
    search_fields = ["snapshot_date", "error_message"]
    readonly_fields = ["started_at", "finished_at", "updated_at"]
    ordering = ["-snapshot_date", "-started_at", "-id"]


@admin.register(BahamutBoardRankingEntry)
class BahamutBoardRankingEntryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "snapshot",
        "rank",
        "board_title",
        "bsn",
        "heat_value",
        "rank_change",
        "is_new_entry",
        "is_rank_rising",
        "is_high_rank",
        "is_hot",
        "selected_for_daily",
    ]
    list_filter = [
        "snapshot",
        "is_game",
        "is_new_entry",
        "is_rank_rising",
        "is_high_rank",
        "is_hot",
        "selected_for_daily",
    ]
    search_fields = ["board_title", "bsn", "board_url", "heat_text"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-snapshot__snapshot_date", "rank", "id"]
