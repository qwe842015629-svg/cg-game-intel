import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_avatar_upload_to(instance, filename):
    """Store avatars in user-specific folders for basic sandbox isolation."""
    user_id = getattr(instance, "user_id", None) or "anonymous"
    suffix = str(filename or "avatar").split("/")[-1].split("\\")[-1]
    return f"avatars/user_{user_id}/{suffix}"


class UserProfile(models.Model):
    class GlobalVisibility(models.IntegerChoices):
        PRIVATE = 0, "Private"
        FOLLOWERS = 1, "Followers"
        PUBLIC = 2, "Public"

    AI_VISIBILITY_PRIVATE = "private"
    AI_VISIBILITY_MEMBERS = "members"
    AI_VISIBILITY_PUBLIC = "public"
    AI_VISIBILITY_CHOICES = [
        (AI_VISIBILITY_PRIVATE, "仅自己可见"),
        (AI_VISIBILITY_MEMBERS, "登录用户可见"),
        (AI_VISIBILITY_PUBLIC, "公开"),
    ]

    AI_ISOLATION_STRICT = "strict"
    AI_ISOLATION_BALANCED = "balanced"
    AI_ISOLATION_CHOICES = [
        (AI_ISOLATION_STRICT, "严格隔离"),
        (AI_ISOLATION_BALANCED, "平衡模式"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to=user_avatar_upload_to, blank=True, null=True, verbose_name="头像")
    avatar_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="头像更新时间")
    display_name = models.CharField(max_length=80, blank=True, default="", verbose_name="显示名称")
    gender = models.CharField(max_length=20, blank=True, default="", verbose_name="性别")
    bio = models.TextField(blank=True, default="", verbose_name="个人介绍")
    sandbox_namespace = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False, verbose_name="用户沙箱命名空间")
    sandbox_enabled = models.BooleanField(default=True, verbose_name="启用用户沙箱")
    ai_content_visibility = models.CharField(
        max_length=20,
        choices=AI_VISIBILITY_CHOICES,
        default=AI_VISIBILITY_PRIVATE,
        verbose_name="AI内容可见范围",
    )
    global_ai_visibility = models.PositiveSmallIntegerField(
        choices=GlobalVisibility.choices,
        default=GlobalVisibility.PUBLIC,
        db_index=True,
        verbose_name="全局 AI 可见范围",
    )
    ai_isolation_mode = models.CharField(
        max_length=20,
        choices=AI_ISOLATION_CHOICES,
        default=AI_ISOLATION_STRICT,
        verbose_name="AI隔离策略",
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="账户余额")
    points = models.IntegerField(default=0, verbose_name="积分")
    vip_level = models.IntegerField(default=0, verbose_name="VIP等级")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "user_profile"
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}的资料"


class UserFollow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_relationships",
        verbose_name="关注者",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_relationships",
        verbose_name="被关注者",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "user_follow"
        verbose_name = "用户关注"
        verbose_name_plural = "用户关注"
        ordering = ["-created_at"]
        unique_together = ("follower", "following")
        constraints = [
            models.CheckConstraint(check=~Q(follower=F("following")), name="user_follow_no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower_id}->{self.following_id}"


class DirectMessageThread(models.Model):
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiated_dm_threads",
        verbose_name="发起人",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_dm_threads",
        verbose_name="接收人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "direct_message_thread"
        verbose_name = "私信会话"
        verbose_name_plural = "私信会话"
        ordering = ["-updated_at"]
        unique_together = ("initiator", "recipient")
        constraints = [
            models.CheckConstraint(check=~Q(initiator=F("recipient")), name="dm_thread_no_self_chat"),
        ]

    def __str__(self):
        return f"dm:{self.initiator_id}->{self.recipient_id}"


class DirectMessage(models.Model):
    thread = models.ForeignKey(
        DirectMessageThread,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="会话",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_direct_messages",
        verbose_name="发送者",
    )
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "direct_message"
        verbose_name = "私信消息"
        verbose_name_plural = "私信消息"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["thread", "created_at"]),
        ]

    def __str__(self):
        return f"dm_msg:{self.thread_id}:{self.sender_id}:{self.id}"


class DirectMessageReadState(models.Model):
    thread = models.ForeignKey(
        DirectMessageThread,
        on_delete=models.CASCADE,
        related_name="read_states",
        verbose_name="会话",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="direct_message_read_states",
        verbose_name="用户",
    )
    last_read_message_id = models.PositiveIntegerField(default=0, verbose_name="最后已读消息ID")
    last_read_at = models.DateTimeField(auto_now=True, verbose_name="最后已读时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "direct_message_read_state"
        verbose_name = "私信已读状态"
        verbose_name_plural = "私信已读状态"
        unique_together = ("thread", "user")
        indexes = [
            models.Index(fields=["user", "thread"]),
            models.Index(fields=["thread", "last_read_message_id"]),
        ]

    def __str__(self):
        return f"dm_read:{self.user_id}:{self.thread_id}:{self.last_read_message_id}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile automatically when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile together with user save operation."""
    if hasattr(instance, "profile"):
        instance.profile.save()
