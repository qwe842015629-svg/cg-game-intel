from rest_framework import serializers

from game_recharge.i18n_utils import localize_text, resolve_request_locale

from .chat_models import ChatAgentConfig, ChatMessage, ChatSession
from .models import ContactMethod, CustomerServiceConfig, FAQ


CONTACT_TYPE_DISPLAY_MAP = {
    "online_chat": {"en": "Live Chat"},
    "email": {"en": "Email Support"},
    "phone": {"en": "Phone Support"},
    "wechat": {"en": "WeChat Support"},
    "custom": {"en": "Custom Contact"},
}

CHAT_STATUS_DISPLAY_MAP = {
    ChatSession.STATUS_AI: {"en": "AI Handling"},
    ChatSession.STATUS_HUMAN: {"en": "Human Agent"},
    ChatSession.STATUS_CLOSED: {"en": "Closed"},
}

CHAT_SENDER_DISPLAY_MAP = {
    ChatMessage.SENDER_USER: {"en": "User"},
    ChatMessage.SENDER_AI: {"en": "AI Assistant"},
    ChatMessage.SENDER_AGENT: {"en": "Agent"},
    ChatMessage.SENDER_SYSTEM: {"en": "System"},
}


def _resolve_serializer_locale(context: dict) -> str:
    request = context.get("request") if isinstance(context, dict) else None
    return resolve_request_locale(request)


def _localized_label(value_key: str, locale: str, fallback: str, mapping: dict) -> str:
    if locale.startswith("en"):
        custom = (mapping.get(value_key) or {}).get("en", "")
        if custom:
            return custom
    return fallback


class ContactMethodSerializer(serializers.ModelSerializer):
    contact_type_display = serializers.CharField(source="get_contact_type_display", read_only=True)

    class Meta:
        model = ContactMethod
        fields = [
            "id",
            "contact_type",
            "contact_type_display",
            "title",
            "description",
            "contact_info",
            "icon",
            "button_text",
            "button_link",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))

        data["title"] = localize_text(instance.title, getattr(instance, "title_i18n", {}), locale)
        data["description"] = localize_text(
            instance.description, getattr(instance, "description_i18n", {}), locale
        )
        data["button_text"] = localize_text(
            instance.button_text, getattr(instance, "button_text_i18n", {}), locale
        )
        data["contact_type_display"] = _localized_label(
            instance.contact_type,
            locale,
            data.get("contact_type_display", ""),
            CONTACT_TYPE_DISPLAY_MAP,
        )
        return data


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "category",
            "is_active",
            "sort_order",
            "view_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["view_count", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))

        data["question"] = localize_text(instance.question, getattr(instance, "question_i18n", {}), locale)
        data["answer"] = localize_text(instance.answer, getattr(instance, "answer_i18n", {}), locale)
        data["category"] = localize_text(instance.category, getattr(instance, "category_i18n", {}), locale)
        return data


class CustomerServiceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerServiceConfig
        fields = [
            "id",
            "page_title",
            "page_description",
            "show_contact_methods",
            "show_faq",
            "faq_title",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))

        data["page_title"] = localize_text(instance.page_title, getattr(instance, "page_title_i18n", {}), locale)
        data["page_description"] = localize_text(
            instance.page_description,
            getattr(instance, "page_description_i18n", {}),
            locale,
        )
        data["faq_title"] = localize_text(instance.faq_title, getattr(instance, "faq_title_i18n", {}), locale)
        return data


class ChatAgentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAgentConfig
        fields = [
            "id",
            "name",
            "is_active",
            "ai_display_name",
            "welcome_message",
            "fallback_message",
            "transfer_keywords",
            "auto_reply_enabled",
            "show_knowledge_panel",
            "max_context_messages",
            "enable_external_ai",
            "api_endpoint",
            "api_model",
            "api_token",
            "api_extra_headers",
            "request_timeout",
            "system_prompt",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_type_display = serializers.CharField(source="get_sender_type_display", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "sender_type",
            "sender_type_display",
            "sender_name",
            "content",
            "metadata",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["sender_type_display"] = _localized_label(
            instance.sender_type,
            locale,
            data.get("sender_type_display", ""),
            CHAT_SENDER_DISPLAY_MAP,
        )
        return data


class ChatSessionPublicSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source="session_key", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_agent_name = serializers.CharField(source="assigned_agent.username", read_only=True, default="")

    class Meta:
        model = ChatSession
        fields = [
            "session_id",
            "status",
            "status_display",
            "visitor_name",
            "is_user_waiting",
            "assigned_agent_name",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["status_display"] = _localized_label(
            instance.status,
            locale,
            data.get("status_display", ""),
            CHAT_STATUS_DISPLAY_MAP,
        )
        return data


class ChatSessionListSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source="session_key", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_agent_name = serializers.CharField(source="assigned_agent.username", read_only=True, default="")
    last_message_preview = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()
    unread_user_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "session_id",
            "visitor_name",
            "visitor_contact",
            "visitor_token",
            "source_page",
            "status",
            "status_display",
            "assigned_agent",
            "assigned_agent_name",
            "is_user_waiting",
            "last_message_at",
            "updated_at",
            "created_at",
            "last_message_preview",
            "last_message_sender",
            "unread_user_count",
        ]

    def _get_latest_message(self, obj):
        latest = getattr(obj, "_latest_message_cache", None)
        if latest is not None:
            return latest
        latest = obj.messages.order_by("-id").first()
        obj._latest_message_cache = latest
        return latest

    def get_last_message_preview(self, obj):
        latest = self._get_latest_message(obj)
        if not latest:
            return ""
        return latest.content[:80]

    def get_last_message_sender(self, obj):
        latest = self._get_latest_message(obj)
        if not latest:
            return ""
        return latest.sender_type

    def get_unread_user_count(self, obj):
        return obj.messages.filter(sender_type=ChatMessage.SENDER_USER, is_read_by_agent=False).count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        data["status_display"] = _localized_label(
            instance.status,
            locale,
            data.get("status_display", ""),
            CHAT_STATUS_DISPLAY_MAP,
        )
        return data


class ChatSessionDetailSerializer(ChatSessionListSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta(ChatSessionListSerializer.Meta):
        fields = ChatSessionListSerializer.Meta.fields + ["messages", "closed_at"]
