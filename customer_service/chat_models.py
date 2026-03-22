import uuid

from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class ChatAgentConfig(models.Model):
    """Configuration for AI-first chat behavior."""

    name = models.CharField(max_length=100, default="Default AI Agent", verbose_name="配置名称")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    ai_display_name = models.CharField(max_length=100, default="AI客服", verbose_name="AI客服显示名称")
    welcome_message = models.TextField(
        default="您好，欢迎来到客服中心。我是 AI 客服，可以先帮您快速处理问题。",
        verbose_name="欢迎语",
    )
    fallback_message = models.TextField(
        default="我已经收到您的问题，正在为您整理答案。若需要人工客服，请发送“转人工”。",
        verbose_name="兜底回复",
    )
    transfer_keywords = models.TextField(
        default="转人工,人工客服,真人客服,人工,客服",
        verbose_name="转人工关键词",
        help_text="用逗号分隔，命中后自动转人工",
    )
    auto_reply_enabled = models.BooleanField(default=True, verbose_name="是否启用 AI 自动回复")
    show_knowledge_panel = models.BooleanField(default=True, verbose_name="是否展示知识索引")
    max_context_messages = models.PositiveIntegerField(default=6, verbose_name="AI上下文消息条数")

    enable_external_ai = models.BooleanField(default=False, verbose_name="启用外部AI接口")
    api_endpoint = models.URLField(blank=True, verbose_name="外部AI接口地址")
    api_model = models.CharField(max_length=120, blank=True, verbose_name="外部AI模型")
    api_token = models.CharField(max_length=255, blank=True, verbose_name="外部AI Token")
    api_extra_headers = models.JSONField(default=dict, blank=True, verbose_name="额外请求头")
    request_timeout = models.PositiveIntegerField(default=15, verbose_name="请求超时(秒)")
    system_prompt = models.TextField(
        blank=True,
        default="你是一个游戏充值网站客服助手，请先基于 FAQ 和站点内容回答，必要时引导转人工。",
        verbose_name="系统提示词",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "AI客服配置"
        verbose_name_plural = "AI客服配置"
        ordering = ["-is_active", "-updated_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            ChatAgentConfig.objects.exclude(pk=self.pk).update(is_active=False)

    @classmethod
    def get_current(cls):
        config = cls.objects.filter(is_active=True).first() or cls.objects.first()
        if config:
            return config
        return cls.objects.create()


class ChatSession(models.Model):
    STATUS_AI = "ai"
    STATUS_HUMAN = "human"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_AI, "AI接待"),
        (STATUS_HUMAN, "人工接待"),
        (STATUS_CLOSED, "已关闭"),
    ]

    session_key = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, verbose_name="会话ID")
    visitor_token = models.CharField(max_length=100, db_index=True, verbose_name="访客标识")
    visitor_name = models.CharField(max_length=100, blank=True, verbose_name="访客昵称")
    visitor_contact = models.CharField(max_length=120, blank=True, verbose_name="访客联系方式")
    source_page = models.CharField(max_length=255, blank=True, verbose_name="来源页面")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_AI, verbose_name="会话状态")
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_service_sessions",
        verbose_name="接待客服",
    )
    last_message_at = models.DateTimeField(null=True, blank=True, verbose_name="最后消息时间")
    last_user_message_at = models.DateTimeField(null=True, blank=True, verbose_name="用户最后发言时间")
    last_agent_message_at = models.DateTimeField(null=True, blank=True, verbose_name="客服最后发言时间")
    is_user_waiting = models.BooleanField(default=False, verbose_name="是否待人工回复")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="关闭时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "在线客服会话"
        verbose_name_plural = "在线客服会话"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "-updated_at"]),
            models.Index(fields=["visitor_token", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.visitor_name or self.visitor_token} ({self.get_status_display()})"


class ChatMessage(models.Model):
    SENDER_USER = "user"
    SENDER_AI = "ai"
    SENDER_AGENT = "agent"
    SENDER_SYSTEM = "system"
    SENDER_CHOICES = [
        (SENDER_USER, "用户"),
        (SENDER_AI, "AI客服"),
        (SENDER_AGENT, "人工客服"),
        (SENDER_SYSTEM, "系统消息"),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="所属会话")
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES, verbose_name="发送者类型")
    sender_name = models.CharField(max_length=100, blank=True, verbose_name="发送者名称")
    content = models.TextField(verbose_name="消息内容")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="扩展数据")
    is_read_by_agent = models.BooleanField(default=False, verbose_name="人工客服是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "在线客服消息"
        verbose_name_plural = "在线客服消息"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["session", "id"]),
            models.Index(fields=["session", "is_read_by_agent"]),
        ]

    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.content[:24]}"

    def save(self, *args, **kwargs):
        if self.sender_type in {self.SENDER_AI, self.SENDER_AGENT, self.SENDER_SYSTEM}:
            self.is_read_by_agent = True
        super().save(*args, **kwargs)
