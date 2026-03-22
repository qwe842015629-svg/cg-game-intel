import json
import logging
import uuid
from typing import Iterable

import requests
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from game_article.models import Article
from game_page.models import GamePage
from game_recharge.i18n_utils import localize_text, localize_text_with_variants, resolve_request_locale

from .chat_models import ChatAgentConfig, ChatMessage, ChatSession
from .models import ContactMethod, CustomerServiceConfig, FAQ
from .serializers import (
    ChatAgentConfigSerializer,
    ChatMessageSerializer,
    ChatSessionDetailSerializer,
    ChatSessionListSerializer,
    ChatSessionPublicSerializer,
    ContactMethodSerializer,
    CustomerServiceConfigSerializer,
    FAQSerializer,
)


User = get_user_model()
logger = logging.getLogger(__name__)
HUMAN_IDLE_RESET_SECONDS = 120


class ContactMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContactMethod.objects.filter(is_active=True)
    serializer_class = ContactMethodSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "id"]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category"]
    ordering_fields = ["sort_order", "view_count", "created_at"]
    ordering = ["sort_order", "-created_at"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CustomerServiceConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomerServiceConfig.objects.all()
    serializer_class = CustomerServiceConfigSerializer

    @action(detail=False, methods=["get"])
    def current(self, request):
        config = CustomerServiceConfig.objects.first()
        if not config:
            config = CustomerServiceConfig(
                page_title="Customer Service Center",
                show_contact_methods=True,
                show_faq=True,
                faq_title="FAQ",
            )
        serializer = self.get_serializer(config)
        return Response(serializer.data)


def _normalize_text(value) -> str:
    return str(value or "").strip()


def _to_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    normalized = str(value).strip().lower()
    if not normalized:
        return default
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _coerce_timeout(value, default: int = 15, min_value: int = 5, max_value: int = 180) -> int:
    try:
        timeout = int(value or default)
    except Exception:
        timeout = default
    return max(min_value, min(max_value, timeout))


def _get_transfer_keywords(config: ChatAgentConfig) -> list[str]:
    raw = config.transfer_keywords.replace("\n", ",")
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def _should_handoff_to_human(message: str, config: ChatAgentConfig) -> bool:
    normalized = _normalize_text(message).lower()
    if not normalized:
        return False
    return any(keyword in normalized for keyword in _get_transfer_keywords(config))


def _serialize_session_messages(messages: Iterable[ChatMessage], request=None) -> list[dict]:
    return ChatMessageSerializer(messages, many=True, context={"request": request}).data


def _localized_game_title(game: GamePage, locale: str) -> str:
    if locale == "zh-TW":
        return localize_text_with_variants(
            locale,
            (getattr(game, "title_tw", ""), {}),
            (getattr(game, "title", ""), getattr(game, "title_i18n", {})),
        )
    return localize_text(getattr(game, "title", ""), getattr(game, "title_i18n", {}), locale)


def _localized_article_title(article: Article, locale: str) -> str:
    return localize_text(getattr(article, "title", ""), getattr(article, "title_i18n", {}), locale)


def _site_index_payload(locale: str) -> dict:
    faq_items = FAQ.objects.filter(is_active=True).order_by("sort_order", "-view_count")[:12]
    game_items = (
        GamePage.objects.filter(status="published")
        .order_by("-is_hot", "sort_order", "-updated_at")
        .only("id", "title", "title_i18n", "title_tw", "slug")[:12]
    )
    article_items = (
        Article.objects.filter(status="published")
        .order_by("-is_top", "-published_at", "-updated_at")
        .only("id", "title", "title_i18n", "slug")[:12]
    )

    return {
        "faqs": [
            {
                "id": faq.id,
                "question": localize_text(faq.question, getattr(faq, "question_i18n", {}), locale),
                "answer": localize_text(faq.answer, getattr(faq, "answer_i18n", {}), locale),
                "category": localize_text(faq.category, getattr(faq, "category_i18n", {}), locale),
            }
            for faq in faq_items
        ],
        "games": [{"id": game.id, "title": _localized_game_title(game, locale), "slug": game.slug} for game in game_items],
        "articles": [
            {"id": article.id, "title": _localized_article_title(article, locale), "slug": article.slug}
            for article in article_items
        ],
    }


def _touch_session(session: ChatSession, sender_type: str, waiting_for_human: bool | None = None):
    now = timezone.now()
    update_fields = ["last_message_at", "updated_at"]
    session.last_message_at = now
    if sender_type == ChatMessage.SENDER_USER:
        session.last_user_message_at = now
        update_fields.append("last_user_message_at")
    else:
        session.last_agent_message_at = now
        update_fields.append("last_agent_message_at")
    if waiting_for_human is not None:
        session.is_user_waiting = waiting_for_human
        update_fields.append("is_user_waiting")
    session.save(update_fields=update_fields)


def _safe_extract_external_ai_answer(payload: dict) -> str:
    if isinstance(payload, dict):
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0] or {}
            message = first.get("message") if isinstance(first, dict) else None
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
        for key in ("answer", "text", "content", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _parse_extra_headers(value) -> dict[str, str]:
    headers = value
    if isinstance(headers, str):
        text = headers.strip()
        if not text:
            headers = {}
        else:
            try:
                headers = json.loads(text)
            except Exception:
                headers = {}
    if not isinstance(headers, dict):
        return {}
    normalized = {}
    for key, item in headers.items():
        if key and item is not None:
            normalized[str(key)] = str(item)
    return normalized


def _external_ai_endpoint_candidates(api_endpoint: str) -> list[str]:
    endpoint = _normalize_text(api_endpoint).rstrip("/")
    if not endpoint:
        return []
    candidates: list[str] = []

    def _append(url: str):
        if url and url not in candidates:
            candidates.append(url)

    _append(endpoint)
    lowered = endpoint.lower()
    if not lowered.endswith("/chat/completions"):
        _append(f"{endpoint}/chat/completions")
        if lowered.endswith("/v1"):
            _append(f"{endpoint}/chat/completions")
        else:
            _append(f"{endpoint}/v1/chat/completions")
    return candidates


def _invoke_external_ai(
    *,
    api_endpoint: str,
    api_model: str,
    api_token: str,
    api_extra_headers: dict | str | None,
    request_timeout: int,
    messages: list[dict],
) -> dict:
    token = _normalize_text(api_token)
    endpoint_candidates = _external_ai_endpoint_candidates(api_endpoint)
    if not endpoint_candidates:
        return {"success": False, "error": "External AI endpoint is not configured.", "endpoint_candidates": []}
    if not token:
        return {"success": False, "error": "External AI token is not configured.", "endpoint_candidates": endpoint_candidates}

    payload = {"messages": messages}
    model = _normalize_text(api_model)
    if model:
        payload["model"] = model

    base_headers = {"Content-Type": "application/json"}
    base_headers.update(_parse_extra_headers(api_extra_headers))
    auth_values = [f"Bearer {token}", token]
    last_error = ""

    for endpoint in endpoint_candidates:
        for auth_value in auth_values:
            headers = dict(base_headers)
            headers["Authorization"] = auth_value
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=_coerce_timeout(request_timeout),
                )
                if response.status_code >= 400:
                    body_preview = (response.text or "")[:220]
                    last_error = f"HTTP {response.status_code}: {body_preview}"
                    if response.status_code in (401, 403, 404, 405):
                        continue
                    continue

                try:
                    body = response.json()
                except Exception:
                    body = {}

                content = _safe_extract_external_ai_answer(body)
                if content:
                    return {
                        "success": True,
                        "content": content,
                        "endpoint": endpoint,
                        "http_status": response.status_code,
                        "auth_scheme": "bearer" if auth_value.startswith("Bearer ") else "raw",
                    }
                last_error = "External AI responded but no usable text was found."
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                continue

    return {
        "success": False,
        "error": last_error or "External AI request failed.",
        "endpoint_candidates": endpoint_candidates,
    }


def _call_external_ai(config: ChatAgentConfig, session: ChatSession, user_text: str) -> tuple[str, dict]:
    if not config.enable_external_ai or not config.api_endpoint:
        return "", {}

    history_qs = session.messages.order_by("-id")[: config.max_context_messages]
    history = list(reversed(history_qs))
    role_map = {
        ChatMessage.SENDER_USER: "user",
        ChatMessage.SENDER_AI: "assistant",
        ChatMessage.SENDER_AGENT: "assistant",
        ChatMessage.SENDER_SYSTEM: "system",
    }
    messages = []
    if config.system_prompt:
        messages.append({"role": "system", "content": config.system_prompt})
    for item in history:
        messages.append({"role": role_map.get(item.sender_type, "user"), "content": item.content})
    messages.append({"role": "user", "content": user_text})

    result = _invoke_external_ai(
        api_endpoint=config.api_endpoint,
        api_model=config.api_model,
        api_token=config.api_token,
        api_extra_headers=config.api_extra_headers,
        request_timeout=config.request_timeout,
        messages=messages,
    )
    if result.get("success"):
        return str(result.get("content") or ""), {
            "source": "external_ai",
            "endpoint": result.get("endpoint"),
            "auth_scheme": result.get("auth_scheme"),
        }

    logger.warning(
        "External AI call failed. endpoint=%s error=%s",
        config.api_endpoint,
        result.get("error"),
    )
    return "", {}


def _faq_reply(user_text: str) -> tuple[str, dict]:
    text = _normalize_text(user_text).lower()
    if not text:
        return "", {}

    tokens = [token for token in text.replace(",", " ").replace(".", " ").split() if len(token) >= 2]
    best_item = None
    best_score = 0

    for faq in FAQ.objects.filter(is_active=True).order_by("sort_order", "-view_count")[:80]:
        question = (faq.question or "").lower()
        answer = (faq.answer or "").lower()
        score = 0
        if text in question and len(text) >= 2:
            score += 5
        for token in tokens:
            if token in question:
                score += 3
            elif token in answer:
                score += 1
        if score > best_score:
            best_item = faq
            best_score = score

    if best_item and best_score >= 3:
        content = f"Based on FAQ:\n{best_item.question}\n\n{best_item.answer}"
        return content, {"source": "faq", "faq_id": best_item.id}
    return "", {}


def _build_ai_reply(session: ChatSession, user_text: str, config: ChatAgentConfig) -> tuple[str, dict]:
    external_reply, external_meta = _call_external_ai(config, session, user_text)
    if external_reply:
        return external_reply, external_meta

    faq_reply, faq_meta = _faq_reply(user_text)
    if faq_reply:
        return faq_reply, faq_meta

    return config.fallback_message, {"source": "fallback"}


def _get_public_session_or_none(session_id: str, visitor_token: str) -> ChatSession | None:
    if not session_id or not visitor_token:
        return None
    try:
        session_uuid = uuid.UUID(str(session_id))
    except ValueError:
        return None
    query = ChatSession.objects.filter(session_key=session_uuid)
    if visitor_token:
        query = query.filter(visitor_token=visitor_token)
    return query.first()


def _auto_reset_human_session_if_idle(session: ChatSession) -> ChatMessage | None:
    """Reset stale human-handoff session back to AI after user idle timeout."""
    if session.status != ChatSession.STATUS_HUMAN:
        return None

    now = timezone.now()
    last_user_at = session.last_user_message_at or session.last_message_at or session.updated_at or session.created_at
    if not last_user_at:
        return None

    idle_seconds = (now - last_user_at).total_seconds()
    if idle_seconds < HUMAN_IDLE_RESET_SECONDS:
        return None

    session.status = ChatSession.STATUS_AI
    session.assigned_agent = None
    session.is_user_waiting = False
    session.save(update_fields=["status", "assigned_agent", "is_user_waiting", "updated_at"])

    reset_message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_SYSTEM,
        sender_name="System",
        content="No new message for over 2 minutes. Switched back to AI support. Send 'human agent' to handoff again.",
        metadata={"kind": "handoff_timeout_reset", "idle_seconds": int(idle_seconds)},
    )
    _touch_session(session, sender_type=reset_message.sender_type, waiting_for_human=False)
    return reset_message


@api_view(["GET"])
@permission_classes([AllowAny])
def chat_knowledge(request):
    config = ChatAgentConfig.get_current()
    locale = resolve_request_locale(request)
    payload = _site_index_payload(locale=locale)
    payload["agent"] = {
        "name": config.ai_display_name,
        "show_knowledge_panel": config.show_knowledge_panel,
        "transfer_keywords": _get_transfer_keywords(config),
    }
    return Response(payload)


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_session_init(request):
    visitor_token = _normalize_text(request.data.get("visitor_token")) or uuid.uuid4().hex
    visitor_name = _normalize_text(request.data.get("visitor_name"))
    visitor_contact = _normalize_text(request.data.get("visitor_contact"))
    source_page = _normalize_text(request.data.get("source_page"))
    session_id = _normalize_text(request.data.get("session_id"))

    session = _get_public_session_or_none(session_id, visitor_token)
    created = False
    if not session:
        session = ChatSession.objects.create(
            visitor_token=visitor_token,
            visitor_name=visitor_name,
            visitor_contact=visitor_contact,
            source_page=source_page,
        )
        created = True
        config = ChatAgentConfig.get_current()
        if config.welcome_message:
            welcome = ChatMessage.objects.create(
                session=session,
                sender_type=ChatMessage.SENDER_AI,
                sender_name=config.ai_display_name,
                content=config.welcome_message,
                metadata={"kind": "welcome"},
            )
            _touch_session(session, welcome.sender_type, waiting_for_human=False)
    else:
        _auto_reset_human_session_if_idle(session)
        changed = []
        if visitor_name and session.visitor_name != visitor_name:
            session.visitor_name = visitor_name
            changed.append("visitor_name")
        if visitor_contact and session.visitor_contact != visitor_contact:
            session.visitor_contact = visitor_contact
            changed.append("visitor_contact")
        if source_page and session.source_page != source_page:
            session.source_page = source_page
            changed.append("source_page")
        if changed:
            changed.append("updated_at")
            session.save(update_fields=changed)

    session_data = ChatSessionPublicSerializer(session, context={"request": request}).data
    messages_data = _serialize_session_messages(session.messages.order_by("id"), request=request)
    return Response(
        {
            "created": created,
            "visitor_token": visitor_token,
            "session": session_data,
            "messages": messages_data,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def chat_session_messages(request, session_id):
    visitor_token = _normalize_text(request.query_params.get("visitor_token"))
    session = _get_public_session_or_none(session_id, visitor_token)
    if not session:
        return Response({"detail": "Session not found or expired."}, status=status.HTTP_404_NOT_FOUND)
    _auto_reset_human_session_if_idle(session)

    since_id_raw = _normalize_text(request.query_params.get("since_id"))
    messages = session.messages.order_by("id")
    if since_id_raw.isdigit():
        messages = messages.filter(id__gt=int(since_id_raw))

    return Response(
        {
            "session": ChatSessionPublicSerializer(session, context={"request": request}).data,
            "messages": _serialize_session_messages(messages, request=request),
            "server_time": timezone.now(),
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_session_send(request, session_id):
    visitor_token = _normalize_text(request.data.get("visitor_token")) or _normalize_text(
        request.query_params.get("visitor_token")
    )
    session = _get_public_session_or_none(session_id, visitor_token)
    if not session:
        return Response({"detail": "Session not found or expired."}, status=status.HTTP_404_NOT_FOUND)

    reset_message = _auto_reset_human_session_if_idle(session)

    if session.status == ChatSession.STATUS_CLOSED:
        return Response({"detail": "This session is closed. Please start a new session."}, status=status.HTTP_400_BAD_REQUEST)

    content = _normalize_text(request.data.get("content"))
    if not content:
        return Response({"detail": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    emitted_messages = [reset_message] if reset_message else []

    user_message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_USER,
        sender_name=session.visitor_name or "User",
        content=content,
    )
    _touch_session(
        session,
        sender_type=ChatMessage.SENDER_USER,
        waiting_for_human=(session.status == ChatSession.STATUS_HUMAN),
    )

    config = ChatAgentConfig.get_current()
    emitted_messages.append(user_message)

    if _should_handoff_to_human(content, config):
        if session.status != ChatSession.STATUS_HUMAN:
            session.status = ChatSession.STATUS_HUMAN
            session.is_user_waiting = True
            session.save(update_fields=["status", "is_user_waiting", "updated_at"])
            handoff_message = ChatMessage.objects.create(
                session=session,
                sender_type=ChatMessage.SENDER_SYSTEM,
                sender_name="System",
                content="Transferred to a human agent. Please wait for a reply.",
                metadata={"kind": "handoff"},
            )
            _touch_session(session, sender_type=handoff_message.sender_type, waiting_for_human=True)
            emitted_messages.append(handoff_message)
        return Response(
            {
                "handoff": True,
                "session": ChatSessionPublicSerializer(session, context={"request": request}).data,
                "messages": _serialize_session_messages(emitted_messages, request=request),
            }
        )

    if session.status == ChatSession.STATUS_AI and config.auto_reply_enabled:
        ai_text, ai_meta = _build_ai_reply(session, content, config)
        ai_message = ChatMessage.objects.create(
            session=session,
            sender_type=ChatMessage.SENDER_AI,
            sender_name=config.ai_display_name,
            content=ai_text,
            metadata=ai_meta,
        )
        _touch_session(session, sender_type=ai_message.sender_type, waiting_for_human=False)
        emitted_messages.append(ai_message)
    else:
        session.is_user_waiting = True
        session.save(update_fields=["is_user_waiting", "updated_at"])

    return Response(
        {
            "handoff": False,
            "session": ChatSessionPublicSerializer(session, context={"request": request}).data,
            "messages": _serialize_session_messages(emitted_messages, request=request),
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_session_handoff(request, session_id):
    visitor_token = _normalize_text(request.data.get("visitor_token")) or _normalize_text(
        request.query_params.get("visitor_token")
    )
    session = _get_public_session_or_none(session_id, visitor_token)
    if not session:
        return Response({"detail": "Session not found or expired."}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    if session.status != ChatSession.STATUS_HUMAN:
        session.status = ChatSession.STATUS_HUMAN
        session.is_user_waiting = True
        session.last_user_message_at = now
        session.save(update_fields=["status", "is_user_waiting", "last_user_message_at", "updated_at"])
        message = ChatMessage.objects.create(
            session=session,
            sender_type=ChatMessage.SENDER_SYSTEM,
            sender_name="System",
            content="Switched to human customer support. Please wait.",
            metadata={"kind": "handoff"},
        )
        _touch_session(session, sender_type=message.sender_type, waiting_for_human=True)
    else:
        session.last_user_message_at = now
        session.save(update_fields=["last_user_message_at", "updated_at"])

    return Response({"session": ChatSessionPublicSerializer(session, context={"request": request}).data})


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_session_resume_ai(request, session_id):
    visitor_token = _normalize_text(request.data.get("visitor_token")) or _normalize_text(
        request.query_params.get("visitor_token")
    )
    session = _get_public_session_or_none(session_id, visitor_token)
    if not session:
        return Response({"detail": "Session not found or expired."}, status=status.HTTP_404_NOT_FOUND)
    if session.status == ChatSession.STATUS_CLOSED:
        return Response({"detail": "This session is closed. Please start a new session."}, status=status.HTTP_400_BAD_REQUEST)

    emitted_messages: list[ChatMessage] = []
    now = timezone.now()
    if session.status != ChatSession.STATUS_AI:
        session.status = ChatSession.STATUS_AI
        session.assigned_agent = None
        session.is_user_waiting = False
        session.last_user_message_at = now
        session.save(
            update_fields=["status", "assigned_agent", "is_user_waiting", "last_user_message_at", "updated_at"]
        )
        message = ChatMessage.objects.create(
            session=session,
            sender_type=ChatMessage.SENDER_SYSTEM,
            sender_name="System",
            content="Human support ended. AI support resumed.",
            metadata={"kind": "resume_ai"},
        )
        _touch_session(session, sender_type=message.sender_type, waiting_for_human=False)
        emitted_messages.append(message)
    else:
        session.last_user_message_at = now
        session.save(update_fields=["last_user_message_at", "updated_at"])

    return Response(
        {
            "session": ChatSessionPublicSerializer(session, context={"request": request}).data,
            "messages": _serialize_session_messages(emitted_messages, request=request),
        }
    )


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_agent_config(request):
    config = ChatAgentConfig.get_current()
    if request.method == "POST":
        serializer = ChatAgentConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(ChatAgentConfigSerializer(config).data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_agent_config_test(request):
    config = ChatAgentConfig.get_current()
    payload = request.data if isinstance(request.data, dict) else {}

    enable_external_ai = _to_bool(payload.get("enable_external_ai"), default=config.enable_external_ai)
    api_endpoint = _normalize_text(payload.get("api_endpoint") or config.api_endpoint)
    api_model = _normalize_text(payload.get("api_model") or config.api_model)
    api_token = _normalize_text(payload.get("api_token") or config.api_token)
    request_timeout = _coerce_timeout(payload.get("request_timeout"), default=config.request_timeout)
    system_prompt = _normalize_text(payload.get("system_prompt") or config.system_prompt)
    api_extra_headers = payload.get("api_extra_headers", config.api_extra_headers)

    if not enable_external_ai:
        return Response(
            {
                "success": False,
                "message": "external_ai_disabled",
                "error": "Please enable the external AI option first.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not api_endpoint:
        return Response(
            {"success": False, "message": "missing_api_endpoint", "error": "External AI endpoint cannot be empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not api_token:
        return Response(
            {"success": False, "message": "missing_api_token", "error": "External AI token cannot be empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": "Please only reply with this JSON: {\"ok\": true}"})

    result = _invoke_external_ai(
        api_endpoint=api_endpoint,
        api_model=api_model,
        api_token=api_token,
        api_extra_headers=api_extra_headers,
        request_timeout=request_timeout,
        messages=messages,
    )
    if result.get("success"):
        return Response(
            {
                "success": True,
                "message": "connection_ok",
                "endpoint": result.get("endpoint"),
                "http_status": result.get("http_status"),
                "auth_scheme": result.get("auth_scheme"),
                "preview": str(result.get("content") or "").strip()[:180],
            }
        )
    return Response(
        {
            "success": False,
            "message": "connection_failed",
            "error": result.get("error") or "External AI request failed.",
            "endpoint_candidates": result.get("endpoint_candidates") or [],
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_sessions(request):
    queryset = ChatSession.objects.select_related("assigned_agent").order_by("-updated_at")

    status_param = _normalize_text(request.query_params.get("status"))
    if status_param in {choice[0] for choice in ChatSession.STATUS_CHOICES}:
        queryset = queryset.filter(status=status_param)

    waiting_only = _normalize_text(request.query_params.get("waiting_only")).lower()
    if waiting_only in {"1", "true", "yes"}:
        queryset = queryset.filter(is_user_waiting=True)

    keyword = _normalize_text(request.query_params.get("q"))
    if keyword:
        queryset = queryset.filter(
            Q(visitor_name__icontains=keyword)
            | Q(visitor_contact__icontains=keyword)
            | Q(visitor_token__icontains=keyword)
            | Q(messages__content__icontains=keyword)
        ).distinct()

    serializer = ChatSessionListSerializer(queryset[:200], many=True, context={"request": request})
    return Response({"results": serializer.data})


def _admin_get_session_or_404(session_id: str) -> ChatSession | None:
    try:
        session_uuid = uuid.UUID(str(session_id))
    except ValueError:
        return None
    return ChatSession.objects.select_related("assigned_agent").filter(session_key=session_uuid).first()


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_session_detail(request, session_id):
    session = _admin_get_session_or_404(session_id)
    if not session:
        return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

    unread_qs = session.messages.filter(sender_type=ChatMessage.SENDER_USER, is_read_by_agent=False)
    unread_count = unread_qs.count()
    if unread_count:
        unread_qs.update(is_read_by_agent=True)
        if session.is_user_waiting:
            session.is_user_waiting = False
            session.save(update_fields=["is_user_waiting", "updated_at"])

    serializer = ChatSessionDetailSerializer(session, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_session_assign(request, session_id):
    session = _admin_get_session_or_404(session_id)
    if not session:
        return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
    if session.status == ChatSession.STATUS_CLOSED:
        return Response({"detail": "Session is closed and cannot be assigned."}, status=status.HTTP_400_BAD_REQUEST)

    agent_id = request.data.get("agent_id")
    if agent_id:
        agent = User.objects.filter(id=agent_id, is_staff=True).first()
        if not agent:
            return Response({"detail": "Target agent does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        agent = request.user

    session.assigned_agent = agent
    session.status = ChatSession.STATUS_HUMAN
    session.is_user_waiting = False
    session.save(update_fields=["assigned_agent", "status", "is_user_waiting", "updated_at"])

    system_message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_SYSTEM,
        sender_name="System",
        content=f"Session assigned to agent: {agent.get_username()}",
        metadata={"kind": "assign", "agent_id": agent.id},
    )
    _touch_session(session, sender_type=system_message.sender_type, waiting_for_human=False)
    return Response({"session": ChatSessionDetailSerializer(session, context={"request": request}).data})


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_session_reply(request, session_id):
    session = _admin_get_session_or_404(session_id)
    if not session:
        return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
    if session.status == ChatSession.STATUS_CLOSED:
        return Response({"detail": "Session is closed and cannot be replied."}, status=status.HTTP_400_BAD_REQUEST)

    content = _normalize_text(request.data.get("content"))
    if not content:
        return Response({"detail": "Reply content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    if session.assigned_agent_id is None:
        session.assigned_agent = request.user
    session.status = ChatSession.STATUS_HUMAN
    session.is_user_waiting = False
    session.save(update_fields=["assigned_agent", "status", "is_user_waiting", "updated_at"])

    sender_name = request.user.get_full_name() or request.user.get_username()
    message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_AGENT,
        sender_name=sender_name,
        content=content,
        metadata={"agent_id": request.user.id},
    )
    _touch_session(session, sender_type=message.sender_type, waiting_for_human=False)

    return Response(
        {
            "session": ChatSessionPublicSerializer(session, context={"request": request}).data,
            "message": ChatMessageSerializer(message).data,
        }
    )


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_session_close(request, session_id):
    session = _admin_get_session_or_404(session_id)
    if not session:
        return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
    if session.status == ChatSession.STATUS_CLOSED:
        return Response({"session": ChatSessionPublicSerializer(session, context={"request": request}).data})

    session.status = ChatSession.STATUS_CLOSED
    session.is_user_waiting = False
    session.closed_at = timezone.now()
    session.save(update_fields=["status", "is_user_waiting", "closed_at", "updated_at"])

    message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_SYSTEM,
        sender_name="System",
        content="Session closed. Please start a new chat if you need further help.",
        metadata={"kind": "close"},
    )
    _touch_session(session, sender_type=message.sender_type, waiting_for_human=False)

    return Response({"session": ChatSessionPublicSerializer(session, context={"request": request}).data})


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_chat_session_set_status(request, session_id):
    session = _admin_get_session_or_404(session_id)
    if not session:
        return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

    status_value = _normalize_text(request.data.get("status"))
    valid_status = {choice[0] for choice in ChatSession.STATUS_CHOICES}
    if status_value not in valid_status:
        return Response({"detail": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    session.status = status_value
    if status_value == ChatSession.STATUS_CLOSED:
        session.closed_at = timezone.now()
        session.is_user_waiting = False
        session.save(update_fields=["status", "closed_at", "is_user_waiting", "updated_at"])
    else:
        if session.closed_at is not None:
            session.closed_at = None
        if status_value == ChatSession.STATUS_AI:
            session.assigned_agent = None
        session.save(update_fields=["status", "closed_at", "assigned_agent", "updated_at"])

    message = ChatMessage.objects.create(
        session=session,
        sender_type=ChatMessage.SENDER_SYSTEM,
        sender_name="System",
        content=f"Session status updated to: {session.get_status_display()}",
        metadata={"kind": "status", "status": status_value},
    )
    _touch_session(session, sender_type=message.sender_type)
    return Response({"session": ChatSessionPublicSerializer(session, context={"request": request}).data})
