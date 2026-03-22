from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ContactMethodViewSet,
    CustomerServiceConfigViewSet,
    FAQViewSet,
    admin_chat_agent_config,
    admin_chat_agent_config_test,
    admin_chat_session_assign,
    admin_chat_session_close,
    admin_chat_session_detail,
    admin_chat_session_reply,
    admin_chat_session_set_status,
    admin_chat_sessions,
    chat_knowledge,
    chat_session_handoff,
    chat_session_init,
    chat_session_messages,
    chat_session_resume_ai,
    chat_session_send,
)


router = DefaultRouter()
router.register(r"contact-methods", ContactMethodViewSet, basename="contact-method")
router.register(r"faqs", FAQViewSet, basename="faq")
router.register(r"config", CustomerServiceConfigViewSet, basename="customer-service-config")


urlpatterns = [
    path("", include(router.urls)),
    path("chat/knowledge/", chat_knowledge, name="customer-chat-knowledge"),
    path("chat/session/init/", chat_session_init, name="customer-chat-session-init"),
    path("chat/session/<uuid:session_id>/messages/", chat_session_messages, name="customer-chat-session-messages"),
    path("chat/session/<uuid:session_id>/send/", chat_session_send, name="customer-chat-session-send"),
    path("chat/session/<uuid:session_id>/handoff/", chat_session_handoff, name="customer-chat-session-handoff"),
    path("chat/session/<uuid:session_id>/resume-ai/", chat_session_resume_ai, name="customer-chat-session-resume-ai"),
    path("admin/chat/config/", admin_chat_agent_config, name="admin-chat-config"),
    path("admin/chat/config/test/", admin_chat_agent_config_test, name="admin-chat-config-test"),
    path("admin/chat/sessions/", admin_chat_sessions, name="admin-chat-sessions"),
    path("admin/chat/sessions/<uuid:session_id>/", admin_chat_session_detail, name="admin-chat-session-detail"),
    path(
        "admin/chat/sessions/<uuid:session_id>/assign/",
        admin_chat_session_assign,
        name="admin-chat-session-assign",
    ),
    path(
        "admin/chat/sessions/<uuid:session_id>/reply/",
        admin_chat_session_reply,
        name="admin-chat-session-reply",
    ),
    path(
        "admin/chat/sessions/<uuid:session_id>/close/",
        admin_chat_session_close,
        name="admin-chat-session-close",
    ),
    path(
        "admin/chat/sessions/<uuid:session_id>/status/",
        admin_chat_session_set_status,
        name="admin-chat-session-status",
    ),
]
