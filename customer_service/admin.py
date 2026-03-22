from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .chat_models import ChatAgentConfig, ChatMessage, ChatSession
from .models import ContactMethod, CustomerServiceConfig, FAQ


@admin.register(ContactMethod)
class ContactMethodAdmin(admin.ModelAdmin):
    list_display = ["contact_type", "title", "contact_info", "is_active", "sort_order", "updated_at"]
    list_editable = ["is_active", "sort_order"]
    list_filter = ["contact_type", "is_active"]
    search_fields = ["title", "description", "contact_info"]
    ordering = ["sort_order", "id"]

    fieldsets = (
        ("基础信息", {"fields": ("contact_type", "title", "description", "contact_info")}),
        ("展示设置", {"fields": ("icon", "button_text", "button_link")}),
        ("状态", {"fields": ("is_active", "sort_order")}),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "is_active", "sort_order", "view_count", "updated_at"]
    list_editable = ["is_active", "sort_order"]
    list_filter = ["category", "is_active"]
    search_fields = ["question", "answer"]
    ordering = ["sort_order", "-created_at"]
    readonly_fields = ["view_count"]

    fieldsets = (
        ("问题内容", {"fields": ("question", "answer", "category")}),
        ("状态", {"fields": ("is_active", "sort_order", "view_count")}),
    )


@admin.register(CustomerServiceConfig)
class CustomerServiceConfigAdmin(admin.ModelAdmin):
    list_display = ["page_title", "show_contact_methods", "show_faq", "updated_at"]

    fieldsets = (
        ("页面设置", {"fields": ("page_title", "page_description")}),
        ("显示选项", {"fields": ("show_contact_methods", "show_faq", "faq_title")}),
    )

    def has_add_permission(self, request):
        return not CustomerServiceConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatAgentConfig)
class ChatAgentConfigAdmin(admin.ModelAdmin):
    change_form_template = "admin/customer_service/chatagentconfig/change_form.html"
    list_display = [
        "name",
        "is_active",
        "ai_display_name",
        "auto_reply_enabled",
        "enable_external_ai",
        "updated_at",
    ]
    list_editable = ["is_active", "auto_reply_enabled", "enable_external_ai"]
    search_fields = ["name", "ai_display_name", "welcome_message", "system_prompt"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("基础", {"fields": ("name", "is_active", "ai_display_name")}),
        ("对话策略", {"fields": ("welcome_message", "fallback_message", "transfer_keywords", "system_prompt")}),
        ("功能控制", {"fields": ("auto_reply_enabled", "show_knowledge_panel", "max_context_messages")}),
        (
            "外部AI接口（可选）",
            {
                "fields": (
                    "enable_external_ai",
                    "api_endpoint",
                    "api_model",
                    "api_token",
                    "api_extra_headers",
                    "request_timeout",
                )
            },
        ),
        ("时间", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_key",
        "visitor_name",
        "status",
        "assigned_agent",
        "is_user_waiting",
        "last_message_at",
        "console_shortcut",
    ]
    list_filter = ["status", "is_user_waiting", "created_at", "assigned_agent"]
    search_fields = ["session_key", "visitor_name", "visitor_contact", "visitor_token"]
    readonly_fields = [
        "session_key",
        "visitor_token",
        "last_message_at",
        "last_user_message_at",
        "last_agent_message_at",
        "closed_at",
        "created_at",
        "updated_at",
    ]
    ordering = ["-updated_at"]

    fieldsets = (
        (
            "访客信息",
            {"fields": ("session_key", "visitor_name", "visitor_contact", "visitor_token", "source_page")},
        ),
        ("会话状态", {"fields": ("status", "assigned_agent", "is_user_waiting", "closed_at")}),
        (
            "时间",
            {
                "fields": (
                    "last_message_at",
                    "last_user_message_at",
                    "last_agent_message_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def console_shortcut(self, obj):
        base = reverse("admin:customer_service_chatsession_console")
        return format_html('<a href="{}?session={}&v=20260220">打开客服台</a>', base, obj.session_key)

    console_shortcut.short_description = "会话台"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "console/",
                self.admin_site.admin_view(self.chat_console_view),
                name="customer_service_chatsession_console",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        console_url = reverse("admin:customer_service_chatsession_console")
        extra_context["chat_console_url"] = f"{console_url}?v=20260220"
        return super().changelist_view(request, extra_context=extra_context)

    def chat_console_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            "title": "在线客服会话台",
            "chat_api_base": "/api/customer-service/admin/chat",
        }
        response = TemplateResponse(request, "admin/customer_service/chat_console.html", context)
        # Avoid stale iframe content in admin hash-tab mode.
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "sender_type", "sender_name", "is_read_by_agent", "created_at"]
    list_filter = ["sender_type", "is_read_by_agent", "created_at"]
    search_fields = ["session__session_key", "sender_name", "content"]
    readonly_fields = ["session", "sender_type", "sender_name", "content", "metadata", "created_at", "is_read_by_agent"]
    ordering = ["-id"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
