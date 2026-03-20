import uuid

from django.conf import settings
from django.db import models


class OperationApproval(models.Model):
    ACTION_SEO_ARTICLE_PUBLISH = "seo_article_publish"
    ACTION_DAILY_ROBOT_RUN = "daily_robot_run"
    ACTION_SERVER_TASK_EXEC = "server_task_exec"
    ACTION_CHOICES = [
        (ACTION_SEO_ARTICLE_PUBLISH, "SEO Article Publish"),
        (ACTION_DAILY_ROBOT_RUN, "Daily Robot Run"),
        (ACTION_SERVER_TASK_EXEC, "Server Task Exec"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXECUTED = "executed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待审批"),
        (STATUS_APPROVED, "已通过"),
        (STATUS_REJECTED, "已驳回"),
        (STATUS_EXECUTED, "已执行"),
        (STATUS_FAILED, "执行失败"),
    ]

    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    action = models.CharField(max_length=64, choices=ACTION_CHOICES, db_index=True)
    target_type = models.CharField(max_length=64, blank=True, default="")
    target_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    risk_level = models.PositiveSmallIntegerField(default=2)
    reason = models.TextField(blank=True, default="")

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ops_requested_approvals",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ops_approved_approvals",
    )
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ops_executed_approvals",
    )

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True)
    client_id = models.CharField(max_length=80, blank=True, default="")
    client_ip = models.CharField(max_length=64, blank=True, default="")

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    error_message = models.TextField(blank=True, default="")
    last_result = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "操作审批单"
        verbose_name_plural = "操作审批单"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["action", "status"]),
            models.Index(fields=["idempotency_key", "action"]),
            models.Index(fields=["requested_at"]),
        ]

    def __str__(self):
        return f"{self.request_id} ({self.action} / {self.status})"


class OperationAuditLog(models.Model):
    EVENT_REQUEST_CREATED = "request_created"
    EVENT_APPROVED = "approved"
    EVENT_REJECTED = "rejected"
    EVENT_EXECUTED = "executed"
    EVENT_FAILED = "failed"
    EVENT_CHOICES = [
        (EVENT_REQUEST_CREATED, "创建申请"),
        (EVENT_APPROVED, "审批通过"),
        (EVENT_REJECTED, "审批驳回"),
        (EVENT_EXECUTED, "执行成功"),
        (EVENT_FAILED, "执行失败"),
    ]

    approval = models.ForeignKey(
        OperationApproval,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ops_audit_logs",
    )
    actor_name = models.CharField(max_length=120, blank=True, default="")
    client_id = models.CharField(max_length=80, blank=True, default="")
    client_ip = models.CharField(max_length=64, blank=True, default="")
    request_snapshot = models.JSONField(default=dict, blank=True)
    result_snapshot = models.JSONField(default=dict, blank=True)
    message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "操作审计日志"
        verbose_name_plural = "操作审计日志"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.approval_id}:{self.event_type}:{self.created_at:%Y-%m-%d %H:%M:%S}"


class DailyRobotRun(models.Model):
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_PARTIAL = "partial"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"
    STATUS_CHOICES = [
        (STATUS_RUNNING, "运行中"),
        (STATUS_COMPLETED, "完成"),
        (STATUS_PARTIAL, "部分完成"),
        (STATUS_FAILED, "失败"),
        (STATUS_SKIPPED, "跳过"),
    ]

    run_key = models.CharField(max_length=64, default="daily_full_cycle", db_index=True)
    run_date = models.DateField(db_index=True)
    trigger_source = models.CharField(max_length=32, default="scheduler", db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_RUNNING, db_index=True)
    summary = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "每日机器人运行记录"
        verbose_name_plural = "每日机器人运行记录"
        ordering = ["-run_date", "-started_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["run_key", "run_date"], name="ops_daily_robot_run_key_date_uniq"),
        ]
        indexes = [
            models.Index(fields=["status", "run_date"]),
            models.Index(fields=["trigger_source", "run_date"]),
        ]

    def __str__(self):
        return f"{self.run_key}:{self.run_date:%Y-%m-%d}:{self.status}"


class DailyRobotConfig(models.Model):
    PUBLISH_STATUS_DRAFT = "draft"
    PUBLISH_STATUS_PUBLISHED = "published"
    PUBLISH_STATUS_CHOICES = [
        (PUBLISH_STATUS_DRAFT, "草稿"),
        (PUBLISH_STATUS_PUBLISHED, "已发布"),
    ]

    config_key = models.CharField(max_length=40, unique=True, default="default")
    is_enabled = models.BooleanField(default=True)
    daily_hour = models.PositiveSmallIntegerField(default=4)
    poll_seconds = models.PositiveIntegerField(default=900)
    max_running_minutes = models.PositiveIntegerField(default=180)
    import_limit = models.PositiveIntegerField(default=30)
    limit_games = models.PositiveIntegerField(default=6)
    posts_min = models.PositiveIntegerField(default=10)
    posts_max = models.PositiveIntegerField(default=20)
    max_attempts_per_game = models.PositiveSmallIntegerField(default=1)
    rewrite_limit = models.PositiveSmallIntegerField(default=1)
    review_threshold = models.PositiveSmallIntegerField(default=78)
    recent_days = models.PositiveSmallIntegerField(default=30)
    publish_status = models.CharField(
        max_length=12,
        choices=PUBLISH_STATUS_CHOICES,
        default=PUBLISH_STATUS_PUBLISHED,
    )
    publish_now = models.BooleanField(default=True)
    actor_username = models.CharField(max_length=120, blank=True, default="admin_root")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ops_daily_robot_configs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "每日自动任务配置"
        verbose_name_plural = "每日自动任务配置"
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"{self.config_key}:{'enabled' if self.is_enabled else 'disabled'}"

    def save(self, *args, **kwargs):
        status = str(getattr(self, "publish_status", "") or "").strip().lower()
        if status not in {self.PUBLISH_STATUS_DRAFT, self.PUBLISH_STATUS_PUBLISHED}:
            status = self.PUBLISH_STATUS_PUBLISHED if bool(getattr(self, "publish_now", True)) else self.PUBLISH_STATUS_DRAFT
        self.publish_status = status
        self.publish_now = status == self.PUBLISH_STATUS_PUBLISHED
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(config_key="default")
        return obj


class BahamutBoardRankingSnapshot(models.Model):
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_PARTIAL = "partial"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_RUNNING, "运行中"),
        (STATUS_COMPLETED, "完成"),
        (STATUS_PARTIAL, "部分完成"),
        (STATUS_FAILED, "失败"),
    ]

    snapshot_date = models.DateField(unique=True, db_index=True)
    trigger_source = models.CharField(max_length=32, default="scheduler", db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_RUNNING, db_index=True)
    total_raw_count = models.PositiveIntegerField(default=0)
    game_count = models.PositiveIntegerField(default=0)
    source_url = models.URLField(default="https://forum.gamer.com.tw/", blank=True)
    summary = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "巴哈排行榜快照"
        verbose_name_plural = "巴哈排行榜快照"
        ordering = ["-snapshot_date", "-started_at", "-id"]
        indexes = [
            models.Index(fields=["status", "snapshot_date"]),
            models.Index(fields=["trigger_source", "snapshot_date"]),
        ]

    def __str__(self):
        return f"{self.snapshot_date:%Y-%m-%d}:{self.status}"


class BahamutBoardRankingEntry(models.Model):
    snapshot = models.ForeignKey(
        BahamutBoardRankingSnapshot,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    rank = models.PositiveIntegerField(db_index=True)
    board_title = models.CharField(max_length=255)
    board_url = models.URLField()
    bsn = models.PositiveIntegerField(db_index=True)
    heat_text = models.CharField(max_length=80, blank=True, default="")
    heat_value = models.PositiveIntegerField(default=0)
    activity_value = models.PositiveIntegerField(default=0)
    is_game = models.BooleanField(default=True)
    previous_rank = models.PositiveIntegerField(null=True, blank=True)
    rank_change = models.IntegerField(default=0)
    is_new_entry = models.BooleanField(default=False)
    is_rank_rising = models.BooleanField(default=False)
    is_high_rank = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)
    selected_for_daily = models.BooleanField(default=False)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "巴哈排行榜条目"
        verbose_name_plural = "巴哈排行榜条目"
        ordering = ["rank", "id"]
        constraints = [
            models.UniqueConstraint(fields=["snapshot", "bsn"], name="ops_bahamut_rank_entry_snapshot_bsn_uniq"),
        ]
        indexes = [
            models.Index(fields=["snapshot", "rank"]),
            models.Index(fields=["snapshot", "selected_for_daily"]),
            models.Index(fields=["snapshot", "is_game"]),
            models.Index(fields=["bsn"]),
        ]

    def __str__(self):
        return f"#{self.rank} {self.board_title} (bsn={self.bsn})"
