from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from game_recharge.i18n_utils import localize_text, resolve_request_locale
from main.models import NovelDraft, NovelWork, PlazaPost

from .models import DirectMessage, DirectMessageReadState, DirectMessageThread, UserFollow, UserProfile
from .serializers import (
    CurrentUserProfileSerializer,
    CurrentUserProfileUpdateSerializer,
    DirectMessageSerializer,
    DirectMessageThreadListResponseSerializer,
    DirectMessageThreadSerializer,
    build_user_brief_payload,
    build_avatar_url,
    UserRelationListResponseSerializer,
    UserFollowStateSerializer,
    UserListSerializer,
    UserPublicProfileResponseSerializer,
    UserProfileSerializer,
    UserSerializer,
)


def _bounded_limit(raw_value, default=20, min_value=1, max_value=50):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, value))


def _safe_short_text(value, max_len=500):
    text = str(value or "").strip()
    if not text:
        return ""
    return text[:max_len]


def _normalize_owner_scope(user):
    return f"user:{user.pk}"


def _owned_by_user(queryset, user):
    owner_scope = _normalize_owner_scope(user)
    return queryset.filter(Q(user=user) | (Q(user__isnull=True) & Q(owner_key=owner_scope))).distinct()


def _target_owned_content(queryset, target_user):
    owner_scope = _normalize_owner_scope(target_user)
    return queryset.filter(Q(user=target_user) | (Q(user__isnull=True) & Q(owner_key=owner_scope))).distinct()


def _viewer_follows_target(viewer, target_user):
    if not getattr(viewer, "is_authenticated", False):
        return False
    if viewer.id == target_user.id:
        return True
    return UserFollow.objects.filter(follower=viewer, following=target_user).exists()


def _content_visibility_scope(*, is_owner, is_follower):
    if is_owner:
        return [
            NovelWork.Visibility.PRIVATE,
            NovelWork.Visibility.FOLLOWERS,
            NovelWork.Visibility.PUBLIC,
        ]
    if is_follower:
        return [NovelWork.Visibility.FOLLOWERS, NovelWork.Visibility.PUBLIC]
    return [NovelWork.Visibility.PUBLIC]


def _relation_user_payload(user, *, request, followed_at):
    profile = getattr(user, "profile", None)
    full_name = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
    display_name = (getattr(profile, "display_name", "") or "").strip()

    return {
        "id": int(user.id),
        "username": str(user.username or ""),
        "name": display_name or full_name or str(user.username or ""),
        "avatar_url": build_avatar_url(request, profile) if profile else "",
        "bio": (getattr(profile, "bio", "") or "").strip(),
        "followed_at": followed_at,
    }


def _collect_published_novel_ids(plaza_post_queryset):
    novel_ids = set()
    rows = plaza_post_queryset.values("source_ref", "source_data")
    for row in rows:
        source_ref = str(row.get("source_ref") or "").strip()
        if source_ref.isdigit():
            novel_ids.add(int(source_ref))

        source_data = row.get("source_data")
        if isinstance(source_data, dict):
            raw_id = source_data.get("id")
            try:
                source_data_id = int(raw_id)
            except (TypeError, ValueError):
                source_data_id = 0
            if source_data_id > 0:
                novel_ids.add(source_data_id)

    return novel_ids


def _safe_localized_text(value, *, locale, max_len=500, depth=0):
    if depth > 4:
        return ""

    if isinstance(value, dict):
        localized = localize_text("", value, locale)
        if localized:
            return str(localized).strip()[:max_len]
        for item in value.values():
            text = _safe_localized_text(item, locale=locale, max_len=max_len, depth=depth + 1)
            if text:
                return text[:max_len]
        return ""

    if isinstance(value, (list, tuple)):
        for item in value:
            text = _safe_localized_text(item, locale=locale, max_len=max_len, depth=depth + 1)
            if text:
                return text[:max_len]
        return ""

    text = str(value or "").strip()
    return text[:max_len]


def _build_public_profile_querysets(request, target_user):
    is_owner = bool(request.user.is_authenticated and request.user.id == target_user.id)
    is_follower = bool(
        request.user.is_authenticated
        and request.user.id != target_user.id
        and _viewer_follows_target(request.user, target_user)
    )
    visible_levels = _content_visibility_scope(is_owner=is_owner, is_follower=is_follower)

    novel_post_qs = _target_owned_content(
        PlazaPost.objects.filter(post_type="novel_work"),
        target_user,
    ).order_by("-updated_at", "-id")
    character_qs = _target_owned_content(
        PlazaPost.objects.filter(post_type="role_card"),
        target_user,
    ).order_by("-updated_at", "-id")

    if not is_owner:
        novel_post_qs = novel_post_qs.filter(visibility__in=visible_levels)
        character_qs = character_qs.filter(visibility__in=visible_levels)

    published_novel_ids = _collect_published_novel_ids(novel_post_qs)
    novel_qs = _target_owned_content(NovelWork.objects.all(), target_user).order_by("-updated_at", "-id")
    if published_novel_ids:
        novel_qs = novel_qs.filter(id__in=published_novel_ids)
    else:
        novel_qs = novel_qs.none()

    if not is_owner:
        novel_qs = novel_qs.filter(visibility__in=visible_levels)

    return {
        "is_owner": is_owner,
        "is_follower": is_follower,
        "novel_qs": novel_qs,
        "character_qs": character_qs,
    }


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户API视图集

    list: 获取用户列表
    retrieve: 获取用户详情
    me: 获取当前登录用户信息
    """

    queryset = User.objects.filter(is_active=True).select_related("profile")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        total_users = User.objects.filter(is_active=True).count()
        return Response(
            {
                "total_users": total_users,
                "active_users": total_users,
                "new_users_today": 0,
            }
        )


class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        payload = CurrentUserProfileSerializer.from_user(request.user, request=request)
        serializer = CurrentUserProfileSerializer(payload)
        return Response(serializer.data)

    def patch(self, request):
        serializer = CurrentUserProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _profile = serializer.save(user=request.user)

        payload = CurrentUserProfileSerializer.from_user(user, request=request)
        output = CurrentUserProfileSerializer(payload)
        return Response(output.data, status=status.HTTP_200_OK)


class CurrentUserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        limit = _bounded_limit(request.query_params.get("limit"), default=20, max_value=60)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        owner_scope = _normalize_owner_scope(user)

        draft_qs = _owned_by_user(NovelDraft.objects.all(), user).order_by("-updated_at", "-id")
        work_qs = _owned_by_user(NovelWork.objects.all(), user).order_by("-updated_at", "-id")
        role_card_qs = _owned_by_user(PlazaPost.objects.filter(post_type="role_card"), user).order_by(
            "-updated_at", "-id"
        )
        ai_post_qs = _owned_by_user(
            PlazaPost.objects.filter(post_type__in=["role_card", "novel_work", "text"]),
            user,
        ).order_by("-updated_at", "-id")

        drafts = []
        for draft in draft_qs[:limit]:
            state = draft.state if isinstance(draft.state, dict) else {}
            drafts.append(
                {
                    "id": draft.id,
                    "title": _safe_short_text(draft.title, 200),
                    "updated_at": draft.updated_at,
                    "created_at": draft.created_at,
                    "state_key_count": len(state.keys()),
                    "state_keys": list(state.keys())[:10],
                }
            )

        works = []
        for work in work_qs[:limit]:
            chapters = work.chapters if isinstance(work.chapters, list) else []
            character_images = work.character_images if isinstance(work.character_images, list) else []
            extra_meta = work.extra_meta if isinstance(work.extra_meta, dict) else {}
            works.append(
                {
                    "id": work.id,
                    "title": _safe_short_text(work.title, 200),
                    "summary": _safe_short_text(work.summary, 400),
                    "cover_image": str(work.cover_image or ""),
                    "chapter_count": len(chapters),
                    "character_image_count": len(character_images),
                    "completion_status": str(extra_meta.get("completion_status") or "draft"),
                    "updated_at": work.updated_at,
                    "created_at": work.created_at,
                }
            )

        role_cards = []
        for post in role_card_qs[:limit]:
            source_data = post.source_data if isinstance(post.source_data, dict) else {}
            role_cards.append(
                {
                    "id": post.id,
                    "post_id": post.id,
                    "name": _safe_short_text(source_data.get("name") or post.author_name or f"角色卡-{post.id}", 120),
                    "description": _safe_short_text(source_data.get("description") or post.content, 500),
                    "avatar": _safe_short_text(source_data.get("avatar") or post.author_avatar, 2000),
                    "gender": _safe_short_text(source_data.get("gender"), 20),
                    "group": _safe_short_text(source_data.get("group"), 60),
                    "source_ref": _safe_short_text(post.source_ref, 128),
                    "updated_at": post.updated_at,
                    "created_at": post.created_at,
                }
            )

        ai_contents = []
        for post in ai_post_qs[:limit]:
            ai_contents.append(
                {
                    "id": post.id,
                    "type": post.post_type,
                    "content": _safe_short_text(post.content, 500),
                    "source_ref": _safe_short_text(post.source_ref, 128),
                    "updated_at": post.updated_at,
                    "created_at": post.created_at,
                }
            )

        payload = {
            "profile": CurrentUserProfileSerializer.from_user(user, request=request),
            "stats": {
                "novel_draft_count": draft_qs.count(),
                "novel_work_count": work_qs.count(),
                "role_card_count": role_card_qs.count(),
                "ai_content_count": ai_post_qs.count(),
            },
            "novel_drafts": drafts,
            "novel_works": works,
            "role_cards": role_cards,
            "ai_contents": ai_contents,
            "sandbox": {
                "enabled": bool(profile.sandbox_enabled),
                "namespace": str(profile.sandbox_namespace),
                "isolation_mode": profile.ai_isolation_mode,
                "visibility": profile.ai_content_visibility,
                "owner_scope": owner_scope,
                "policies": [
                    "strict_user_scope",
                    "no_cross_user_data_query",
                    "profile_endpoint_ignores_client_id",
                ],
            },
        }
        return Response(payload, status=status.HTTP_200_OK)


class UserPublicProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        target_user = get_object_or_404(
            User.objects.filter(is_active=True).select_related("profile"),
            pk=user_id,
        )

        scoped = _build_public_profile_querysets(request, target_user)

        payload = {
            "user": target_user,
            "follower_count": UserFollow.objects.filter(following=target_user).count(),
            "following_count": UserFollow.objects.filter(follower=target_user).count(),
            "is_owner": scoped["is_owner"],
            "is_following": scoped["is_follower"],
            "novels": scoped["novel_qs"],
            "characters": scoped["character_qs"],
        }
        serializer = UserPublicProfileResponseSerializer(payload, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPublicNovelWorkDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id, novel_id):
        target_user = get_object_or_404(
            User.objects.filter(is_active=True).select_related("profile"),
            pk=user_id,
        )
        scoped = _build_public_profile_querysets(request, target_user)
        work = get_object_or_404(scoped["novel_qs"], pk=novel_id)
        locale = resolve_request_locale(request)

        raw_chapters = work.chapters if isinstance(work.chapters, list) else []
        chapters = []
        for index, item in enumerate(raw_chapters):
            if not isinstance(item, dict):
                continue
            try:
                chapter_no = int(item.get("chapter_no") or (index + 1))
            except (TypeError, ValueError):
                chapter_no = index + 1
            chapters.append(
                {
                    "chapter_no": chapter_no,
                    "title": _safe_localized_text(
                        item.get("title"),
                        locale=locale,
                        max_len=220,
                    ),
                    "content": _safe_localized_text(
                        item.get("content"),
                        locale=locale,
                        max_len=120000,
                    ),
                }
            )

        extra_meta = work.extra_meta if isinstance(work.extra_meta, dict) else {}
        completion_status = _safe_localized_text(extra_meta.get("completion_status"), locale=locale, max_len=40) or "draft"

        payload = {
            "id": work.id,
            "user_id": target_user.id,
            "title": _safe_localized_text(work.title, locale=locale, max_len=200),
            "summary": _safe_localized_text(work.summary, locale=locale, max_len=12000),
            "cover_image": _safe_localized_text(work.cover_image, locale=locale, max_len=2000),
            "visibility": int(work.visibility),
            "completion_status": completion_status,
            "chapter_count": len(chapters),
            "chapters": chapters,
            "created_at": work.created_at,
            "updated_at": work.updated_at,
        }
        return Response(payload, status=status.HTTP_200_OK)


class UserPublicRoleCardDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id, character_id):
        target_user = get_object_or_404(
            User.objects.filter(is_active=True).select_related("profile"),
            pk=user_id,
        )
        scoped = _build_public_profile_querysets(request, target_user)
        post = get_object_or_404(scoped["character_qs"], pk=character_id)
        locale = resolve_request_locale(request)

        source_data = post.source_data if isinstance(post.source_data, dict) else {}
        first_message_raw = source_data.get("firstMessage")
        if first_message_raw in (None, ""):
            first_message_raw = source_data.get("first_message")

        payload = {
            "id": post.id,
            "post_id": post.id,
            "user_id": target_user.id,
            "name": _safe_localized_text(
                source_data.get("name") or post.author_name or f"Role Card {post.id}",
                locale=locale,
                max_len=220,
            ),
            "description": _safe_localized_text(
                source_data.get("description") or post.content,
                locale=locale,
                max_len=12000,
            ),
            "content": _safe_localized_text(post.content, locale=locale, max_len=12000),
            "avatar": _safe_localized_text(
                source_data.get("avatar") or post.author_avatar,
                locale=locale,
                max_len=2000,
            ),
            "group": _safe_localized_text(source_data.get("group"), locale=locale, max_len=120),
            "gender": _safe_localized_text(source_data.get("gender"), locale=locale, max_len=40),
            "first_message": _safe_localized_text(first_message_raw, locale=locale, max_len=12000),
            "source_ref": _safe_localized_text(post.source_ref, locale=locale, max_len=128),
            "visibility": int(post.visibility),
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }
        return Response(payload, status=status.HTTP_200_OK)


class UserFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _target(self, user_id):
        return get_object_or_404(User.objects.filter(is_active=True), pk=user_id)

    def _state_payload(self, request_user, target_user):
        return {
            "target_user_id": target_user.id,
            "is_following": UserFollow.objects.filter(follower=request_user, following=target_user).exists(),
            "follower_count": UserFollow.objects.filter(following=target_user).count(),
            "following_count": UserFollow.objects.filter(follower=target_user).count(),
        }

    def get(self, request, user_id):
        target_user = self._target(user_id)
        payload = self._state_payload(request.user, target_user)
        serializer = UserFollowStateSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        target_user = self._target(user_id)
        if request.user.id == target_user.id:
            raise PermissionDenied("You cannot follow yourself.")

        _, created = UserFollow.objects.get_or_create(follower=request.user, following=target_user)
        payload = self._state_payload(request.user, target_user)
        serializer = UserFollowStateSerializer(payload)
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=response_status)

    def delete(self, request, user_id):
        target_user = self._target(user_id)
        UserFollow.objects.filter(follower=request.user, following=target_user).delete()
        payload = self._state_payload(request.user, target_user)
        serializer = UserFollowStateSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRelationListView(APIView):
    permission_classes = [permissions.AllowAny]

    def _target(self, user_id):
        return get_object_or_404(User.objects.filter(is_active=True).select_related("profile"), pk=user_id)

    def get(self, request, user_id, relation_mode):
        mode = str(relation_mode or "").strip().lower()
        if mode not in {"followers", "following"}:
            return Response({"detail": "relation_mode must be followers or following"}, status=status.HTTP_400_BAD_REQUEST)

        target_user = self._target(user_id)
        limit = _bounded_limit(request.query_params.get("limit"), default=100, max_value=300)

        if mode == "followers":
            relation_qs = (
                UserFollow.objects.filter(following=target_user)
                .select_related("follower", "follower__profile")
                .order_by("-created_at", "-id")
            )
            items = [
                _relation_user_payload(relation.follower, request=request, followed_at=relation.created_at)
                for relation in relation_qs[:limit]
            ]
        else:
            relation_qs = (
                UserFollow.objects.filter(follower=target_user)
                .select_related("following", "following__profile")
                .order_by("-created_at", "-id")
            )
            items = [
                _relation_user_payload(relation.following, request=request, followed_at=relation.created_at)
                for relation in relation_qs[:limit]
            ]

        payload = {
            "user_id": target_user.id,
            "mode": mode,
            "total": relation_qs.count(),
            "items": items,
        }
        serializer = UserRelationListResponseSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDirectMessageThreadsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        limit = _bounded_limit(request.query_params.get("limit"), default=30, max_value=100)

        thread_qs = (
            DirectMessageThread.objects.filter(Q(initiator=request.user) | Q(recipient=request.user))
            .select_related("initiator", "initiator__profile", "recipient", "recipient__profile")
            .order_by("-updated_at", "-id")
        )
        threads = list(thread_qs[:limit])
        thread_ids = [thread.id for thread in threads]

        last_message_map = {}
        if thread_ids:
            rows = (
                DirectMessage.objects.filter(thread_id__in=thread_ids)
                .select_related("sender", "sender__profile")
                .order_by("thread_id", "-id")
            )
            for row in rows:
                if row.thread_id not in last_message_map:
                    last_message_map[row.thread_id] = row

        read_state_map = {
            item.thread_id: item.last_read_message_id
            for item in DirectMessageReadState.objects.filter(user=request.user, thread_id__in=thread_ids)
        }

        total_unread_threads = 0
        total_unread_messages = 0
        thread_items = []
        for thread in threads:
            peer = thread.recipient if thread.initiator_id == request.user.id else thread.initiator
            peer_payload = build_user_brief_payload(peer, request=request)
            last_read_message_id = int(read_state_map.get(thread.id) or 0)
            unread_count = DirectMessage.objects.filter(thread=thread, id__gt=last_read_message_id).exclude(
                sender=request.user
            ).count()
            if unread_count > 0:
                total_unread_threads += 1
                total_unread_messages += unread_count

            thread_items.append(
                {
                    "thread": thread,
                    "peer": peer_payload,
                    "last_message": last_message_map.get(thread.id),
                    "unread_count": unread_count,
                }
            )

        payload = {
            "threads": thread_items,
            "total_unread_threads": total_unread_threads,
            "total_unread_messages": total_unread_messages,
        }
        serializer = DirectMessageThreadListResponseSerializer(payload, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDirectMessageInitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User.objects.filter(is_active=True), pk=user_id)

        if request.user.id == target_user.id:
            return Response({"detail": "Cannot start direct message with yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Reuse any existing thread in either direction so users can continue
        # chatting even if the original initiator was the other side.
        thread = (
            DirectMessageThread.objects.filter(
                Q(initiator=request.user, recipient=target_user)
                | Q(initiator=target_user, recipient=request.user)
            )
            .order_by("-updated_at", "-id")
            .first()
        )
        created = False
        if thread is None:
            if not UserFollow.objects.filter(follower=request.user, following=target_user).exists():
                raise PermissionDenied("Follow the user first before initiating a private chat.")

            thread, created = DirectMessageThread.objects.get_or_create(
                initiator=request.user,
                recipient=target_user,
            )
        payload = {
            "created": created,
            "thread": DirectMessageThreadSerializer(thread).data,
        }
        return Response(payload, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UserDirectMessageMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _resolve_thread(self, request, thread_id: int) -> DirectMessageThread:
        thread = get_object_or_404(DirectMessageThread, pk=thread_id)
        if request.user.id not in {thread.initiator_id, thread.recipient_id}:
            raise PermissionDenied("You do not have access to this direct message thread.")
        return thread

    def _mark_thread_read(self, user, thread: DirectMessageThread):
        last_message = DirectMessage.objects.filter(thread=thread).order_by("-id").values_list("id", flat=True).first()
        last_read_message_id = int(last_message or 0)
        DirectMessageReadState.objects.update_or_create(
            thread=thread,
            user=user,
            defaults={"last_read_message_id": last_read_message_id},
        )
        return last_read_message_id

    def get(self, request, thread_id: int):
        thread = self._resolve_thread(request, thread_id)
        limit = _bounded_limit(request.query_params.get("limit"), default=60, max_value=200)
        before_id = request.query_params.get("before_id")
        mark_read = str(request.query_params.get("mark_read") or "").strip().lower() in {"1", "true", "yes"}

        queryset = DirectMessage.objects.filter(thread=thread).select_related("sender", "sender__profile")
        try:
            before_num = int(before_id)
        except (TypeError, ValueError):
            before_num = 0
        if before_num > 0:
            queryset = queryset.filter(id__lt=before_num)

        rows = list(queryset.order_by("-id")[:limit])
        rows.reverse()
        if mark_read:
            self._mark_thread_read(request.user, thread)
        serializer = DirectMessageSerializer(rows, many=True, context={"request": request})
        return Response(
            {
                "thread": DirectMessageThreadSerializer(thread).data,
                "messages": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, thread_id: int):
        thread = self._resolve_thread(request, thread_id)
        content = str(request.data.get("content") or "").strip()
        if not content:
            return Response({"detail": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        content = content[:2000]

        message = DirectMessage.objects.create(
            thread=thread,
            sender=request.user,
            content=content,
        )
        DirectMessageReadState.objects.update_or_create(
            thread=thread,
            user=request.user,
            defaults={"last_read_message_id": message.id},
        )
        thread.save(update_fields=["updated_at"])
        serializer = DirectMessageSerializer(message, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDirectMessageReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, thread_id: int):
        thread = get_object_or_404(DirectMessageThread, pk=thread_id)
        if request.user.id not in {thread.initiator_id, thread.recipient_id}:
            raise PermissionDenied("You do not have access to this direct message thread.")

        last_message = DirectMessage.objects.filter(thread=thread).order_by("-id").values_list("id", flat=True).first()
        last_read_message_id = int(last_message or 0)
        DirectMessageReadState.objects.update_or_create(
            thread=thread,
            user=request.user,
            defaults={"last_read_message_id": last_read_message_id},
        )
        return Response(
            {
                "thread_id": thread.id,
                "last_read_message_id": last_read_message_id,
                "unread_count": 0,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    用户资料API视图集

    该通用接口仅供后台/管理场景；普通用户请走 /api/users/me/profile/。
    """

    queryset = UserProfile.objects.all().select_related("user")
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def _assert_staff_write(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("普通用户请使用 /api/users/me/profile/ 更新资料。")

    def create(self, request, *args, **kwargs):
        self._assert_staff_write(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._assert_staff_write(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._assert_staff_write(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._assert_staff_write(request)
        return super().destroy(request, *args, **kwargs)
