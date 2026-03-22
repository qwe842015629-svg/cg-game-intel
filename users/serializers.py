from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.models import User

from main.models import NovelWork, PlazaPost

from .models import DirectMessage, DirectMessageReadState, DirectMessageThread, UserFollow, UserProfile


MAX_AVATAR_SIZE = 5 * 1024 * 1024
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def build_avatar_url(request, profile: UserProfile) -> str:
    if not profile or not profile.avatar:
        return ""

    url = profile.avatar.url
    if request is not None:
        try:
            url = request.build_absolute_uri(url)
        except Exception:
            pass

    stamp_source = profile.avatar_updated_at or profile.updated_at
    if stamp_source:
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}v={int(stamp_source.timestamp())}"
    return url


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "avatar",
            "avatar_url",
            "display_name",
            "gender",
            "bio",
            "sandbox_namespace",
            "sandbox_enabled",
            "ai_content_visibility",
            "global_ai_visibility",
            "ai_isolation_mode",
            "balance",
            "points",
            "vip_level",
            "created_at",
            "updated_at",
        ]
        # Keep financial and sandbox policy fields read-only for normal profile API updates.
        read_only_fields = [
            "sandbox_namespace",
            "sandbox_enabled",
            "ai_content_visibility",
            "global_ai_visibility",
            "ai_isolation_mode",
            "balance",
            "points",
            "vip_level",
            "created_at",
            "updated_at",
            "avatar_url",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        return build_avatar_url(request, obj)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    profile = UserProfileSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "name",
            "avatar_url",
            "gender",
            "bio",
            "is_active",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "date_joined", "is_active"]

    def get_name(self, obj):
        if hasattr(obj, "profile") and obj.profile.display_name:
            return obj.profile.display_name
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full_name or obj.username

    def get_avatar_url(self, obj):
        if not hasattr(obj, "profile"):
            return ""
        request = self.context.get("request")
        return build_avatar_url(request, obj.profile)

    def get_gender(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.gender or ""
        return ""

    def get_bio(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.bio or ""
        return ""


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器（简化版）"""

    balance = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    vip_level = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "name",
            "is_active",
            "date_joined",
            "balance",
            "points",
            "vip_level",
        ]

    def get_balance(self, obj):
        if hasattr(obj, "profile"):
            return str(obj.profile.balance)
        return "0.00"

    def get_points(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.points
        return 0

    def get_vip_level(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.vip_level
        return 0

    def get_name(self, obj):
        if hasattr(obj, "profile") and obj.profile.display_name:
            return obj.profile.display_name
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full_name or obj.username


class CurrentUserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    sandbox_namespace = serializers.CharField(read_only=True)
    sandbox_enabled = serializers.BooleanField(read_only=True)
    ai_content_visibility = serializers.CharField(read_only=True)
    global_ai_visibility = serializers.IntegerField(read_only=True)
    ai_isolation_mode = serializers.CharField(read_only=True)
    balance = serializers.CharField(read_only=True)
    points = serializers.IntegerField(read_only=True)
    vip_level = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    @staticmethod
    def from_user(user: User, request=None):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        name = profile.display_name or f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": name,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "phone": profile.phone or "",
            "gender": profile.gender or "",
            "bio": profile.bio or "",
            "avatar_url": build_avatar_url(request, profile),
            "sandbox_namespace": str(profile.sandbox_namespace),
            "sandbox_enabled": bool(profile.sandbox_enabled),
            "ai_content_visibility": profile.ai_content_visibility,
            "global_ai_visibility": profile.global_ai_visibility,
            "ai_isolation_mode": profile.ai_isolation_mode,
            "balance": str(profile.balance),
            "points": profile.points,
            "vip_level": profile.vip_level,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }


class CurrentUserProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    gender = serializers.CharField(required=False, allow_blank=True, max_length=20)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
    avatar = serializers.ImageField(required=False, allow_null=True)
    remove_avatar = serializers.BooleanField(required=False, default=False)
    sandbox_enabled = serializers.BooleanField(required=False)
    ai_content_visibility = serializers.ChoiceField(
        required=False,
        choices=UserProfile.AI_VISIBILITY_CHOICES,
    )
    global_ai_visibility = serializers.ChoiceField(
        required=False,
        choices=UserProfile.GlobalVisibility.choices,
    )

    def validate_avatar(self, value):
        if value is None:
            return value

        content_type = str(getattr(value, "content_type", "") or "").lower()
        if content_type and content_type not in ALLOWED_AVATAR_TYPES:
            raise serializers.ValidationError("仅支持 jpg/png/webp/gif 格式头像。")

        size = int(getattr(value, "size", 0) or 0)
        if size > MAX_AVATAR_SIZE:
            raise serializers.ValidationError("头像文件大小不能超过 5MB。")
        return value

    def save(self, *, user: User):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = self.validated_data
        user_fields_to_update = []
        profile_fields_to_update = []

        if "name" in data:
            profile.display_name = str(data.get("name") or "").strip()[:80]
            profile_fields_to_update.append("display_name")

        if "first_name" in data:
            user.first_name = str(data.get("first_name") or "").strip()[:30]
            user_fields_to_update.append("first_name")

        if "last_name" in data:
            user.last_name = str(data.get("last_name") or "").strip()[:30]
            user_fields_to_update.append("last_name")

        if "phone" in data:
            profile.phone = str(data.get("phone") or "").strip()[:20]
            profile_fields_to_update.append("phone")

        if "gender" in data:
            profile.gender = str(data.get("gender") or "").strip()[:20]
            profile_fields_to_update.append("gender")

        if "bio" in data:
            profile.bio = str(data.get("bio") or "").strip()[:500]
            profile_fields_to_update.append("bio")

        if "sandbox_enabled" in data:
            profile.sandbox_enabled = bool(data.get("sandbox_enabled"))
            profile_fields_to_update.append("sandbox_enabled")

        if "ai_content_visibility" in data:
            profile.ai_content_visibility = str(data.get("ai_content_visibility"))
            profile_fields_to_update.append("ai_content_visibility")

        if "global_ai_visibility" in data:
            profile.global_ai_visibility = int(data.get("global_ai_visibility"))
            profile_fields_to_update.append("global_ai_visibility")

        remove_avatar = bool(data.get("remove_avatar"))
        avatar = data.get("avatar")
        if remove_avatar:
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = None
            profile.avatar_updated_at = timezone.now()
            profile_fields_to_update.extend(["avatar", "avatar_updated_at"])
        elif avatar is not None:
            profile.avatar = avatar
            profile.avatar_updated_at = timezone.now()
            profile_fields_to_update.extend(["avatar", "avatar_updated_at"])

        if user_fields_to_update:
            user.save(update_fields=user_fields_to_update)

        if profile_fields_to_update:
            update_fields = list(dict.fromkeys(profile_fields_to_update + ["updated_at"]))
            profile.save(update_fields=update_fields)

        return user, profile


class PublicProfileUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    global_ai_visibility = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "avatar_url",
            "bio",
            "global_ai_visibility",
        ]

    def get_name(self, obj):
        if hasattr(obj, "profile") and obj.profile.display_name:
            return obj.profile.display_name
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full_name or obj.username

    def get_avatar_url(self, obj):
        if not hasattr(obj, "profile"):
            return ""
        request = self.context.get("request")
        return build_avatar_url(request, obj.profile)

    def get_bio(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.bio or ""
        return ""

    def get_global_ai_visibility(self, obj):
        if hasattr(obj, "profile"):
            return int(obj.profile.global_ai_visibility)
        return int(UserProfile.GlobalVisibility.PUBLIC)


class ProfileNovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelWork
        fields = [
            "id",
            "title",
            "summary",
            "cover_image",
            "visibility",
            "created_at",
            "updated_at",
        ]


class ProfileCharacterSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = PlazaPost
        fields = [
            "id",
            "name",
            "description",
            "avatar",
            "source_ref",
            "visibility",
            "created_at",
            "updated_at",
        ]

    def _source_data(self, obj):
        return obj.source_data if isinstance(obj.source_data, dict) else {}

    def get_name(self, obj):
        data = self._source_data(obj)
        fallback = obj.author_name or f"Role Card {obj.id}"
        return str(data.get("name") or fallback)[:120]

    def get_description(self, obj):
        data = self._source_data(obj)
        fallback = obj.content or ""
        return str(data.get("description") or fallback)[:500]

    def get_avatar(self, obj):
        data = self._source_data(obj)
        return str(data.get("avatar") or obj.author_avatar or "")[:2000]


class UserPublicProfileResponseSerializer(serializers.Serializer):
    user = PublicProfileUserSerializer(read_only=True)
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_owner = serializers.BooleanField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)
    novels = ProfileNovelSerializer(read_only=True, many=True)
    characters = ProfileCharacterSerializer(read_only=True, many=True)


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserFollowStateSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)


class UserRelationItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    followed_at = serializers.DateTimeField(read_only=True)


class UserRelationListResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(read_only=True)
    mode = serializers.ChoiceField(choices=["followers", "following"], read_only=True)
    total = serializers.IntegerField(read_only=True)
    items = UserRelationItemSerializer(read_only=True, many=True)


def build_user_brief_payload(user: User, request=None):
    profile = getattr(user, "profile", None)
    if profile and profile.display_name:
        name = profile.display_name
    else:
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        name = full_name or user.username

    return {
        "id": int(user.id),
        "username": str(user.username or ""),
        "name": str(name or ""),
        "avatar_url": build_avatar_url(request, profile) if profile else "",
    }


class DirectMessageThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessageThread
        fields = ["id", "initiator", "recipient", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = DirectMessage
        fields = [
            "id",
            "thread",
            "sender",
            "sender_name",
            "sender_avatar_url",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "thread", "sender", "sender_name", "sender_avatar_url", "created_at", "updated_at"]

    def get_sender_name(self, obj):
        sender = obj.sender
        if hasattr(sender, "profile") and sender.profile.display_name:
            return sender.profile.display_name
        full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        return full_name or sender.username

    def get_sender_avatar_url(self, obj):
        if not hasattr(obj.sender, "profile"):
            return ""
        request = self.context.get("request")
        return build_avatar_url(request, obj.sender.profile)


class DirectMessagePeerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)


class DirectMessageThreadSummarySerializer(serializers.Serializer):
    thread = DirectMessageThreadSerializer(read_only=True)
    peer = DirectMessagePeerSerializer(read_only=True)
    last_message = DirectMessageSerializer(read_only=True, allow_null=True)
    unread_count = serializers.IntegerField(read_only=True)


class DirectMessageThreadListResponseSerializer(serializers.Serializer):
    threads = DirectMessageThreadSummarySerializer(read_only=True, many=True)
    total_unread_threads = serializers.IntegerField(read_only=True)
    total_unread_messages = serializers.IntegerField(read_only=True)


class DirectMessageThreadReadStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessageReadState
        fields = ["thread", "user", "last_read_message_id", "last_read_at", "created_at"]
        read_only_fields = ["thread", "user", "last_read_message_id", "last_read_at", "created_at"]
