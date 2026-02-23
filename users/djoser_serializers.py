from django.contrib.auth import authenticate, get_user_model
from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    TokenCreateSerializer,
    UserCreatePasswordRetypeSerializer,
    UserCreateSerializer,
)
from rest_framework import serializers


User = get_user_model()


class UsernameFallbackMixin:
    """Ensure username is always present for Django default User model."""

    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def _sanitize_username(self, value: str) -> str:
        raw = (value or "").strip()
        if not raw:
            return ""
        filtered = "".join(ch for ch in raw if ch.isalnum() or ch in ("_", "-", "."))
        return filtered.strip("._-")

    def _build_unique_username(self, preferred: str) -> str:
        base = self._sanitize_username(preferred) or "user"
        base = base[:30]
        candidate = base
        index = 1
        while User.objects.filter(username=candidate).exists():
            suffix = f"_{index}"
            candidate = f"{base[: max(1, 30 - len(suffix))]}{suffix}"
            index += 1
        return candidate

    def validate(self, attrs):
        attrs = super().validate(attrs)

        username = str(
            attrs.get("username")
            or self.initial_data.get("username")
            or self.initial_data.get("name")
            or ""
        ).strip()
        if not username:
            email = str(attrs.get("email") or self.initial_data.get("email") or "").strip()
            username = email.split("@", 1)[0] if email else ""

        attrs["username"] = self._build_unique_username(username)
        return attrs


class EmailLoginUserCreateSerializer(UsernameFallbackMixin, UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            djoser_settings.USER_ID_FIELD,
            djoser_settings.LOGIN_FIELD,
            "username",
            "password",
        )
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            djoser_settings.LOGIN_FIELD: {"required": True, "allow_blank": False},
        }


class EmailLoginUserCreatePasswordRetypeSerializer(
    UsernameFallbackMixin, UserCreatePasswordRetypeSerializer
):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = (
            djoser_settings.USER_ID_FIELD,
            djoser_settings.LOGIN_FIELD,
            "username",
            "password",
        )
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            djoser_settings.LOGIN_FIELD: {"required": True, "allow_blank": False},
        }


class EmailLoginTokenCreateSerializer(TokenCreateSerializer):
    """Support email/username login fallback across mixed deployment settings."""

    default_error_messages = {
        "invalid_credentials": "邮箱或密码错误。",
        "inactive_account": "账号未激活，请先完成邮箱激活。",
    }

    @staticmethod
    def _append_candidate(
        bucket: list[tuple[str, str]], seen: set[str], *, field: str, value: str
    ) -> None:
        field_text = str(field or "").strip()
        value_text = str(value or "").strip()
        if not field_text or not value_text:
            return
        key = f"{field_text}:{value_text}"
        if key in seen:
            return
        seen.add(key)
        bucket.append((field_text, value_text))

    def _build_identity_candidates(self, attrs) -> list[tuple[str, str]]:
        configured_field = str(getattr(djoser_settings, "LOGIN_FIELD", "email") or "email").strip()
        identity = str(
            attrs.get(configured_field)
            or attrs.get("email")
            or attrs.get("username")
            or self.initial_data.get(configured_field)
            or self.initial_data.get("email")
            or self.initial_data.get("username")
            or ""
        ).strip()
        if not identity:
            return []

        identity_lower = identity.lower()
        candidates: list[tuple[str, str]] = []
        seen: set[str] = set()

        self._append_candidate(candidates, seen, field=configured_field, value=identity)
        if identity_lower != identity:
            self._append_candidate(candidates, seen, field=configured_field, value=identity_lower)

        # Always keep email/username fallback compatible with old and new deployments.
        self._append_candidate(candidates, seen, field="email", value=identity_lower)
        self._append_candidate(candidates, seen, field="username", value=identity)
        if identity_lower != identity:
            self._append_candidate(candidates, seen, field="username", value=identity_lower)
        if "@" in identity_lower:
            self._append_candidate(candidates, seen, field="username", value=identity_lower.split("@", 1)[0])

        return candidates

    @staticmethod
    def _resolve_existing_user(field: str, value: str):
        if field == "email":
            return User.objects.filter(email__iexact=value).first()
        return User.objects.filter(**{field: value}).first()

    def validate(self, attrs):
        password = str(attrs.get("password") or self.initial_data.get("password") or "")
        if not password:
            self.fail("invalid_credentials")

        identity_candidates = self._build_identity_candidates(attrs)
        if not identity_candidates:
            self.fail("invalid_credentials")

        inactive_user = None
        request = self.context.get("request")

        for field, value in identity_candidates:
            self.user = authenticate(request=request, password=password, **{field: value})
            if self.user and self.user.is_active:
                return attrs
            if self.user and not self.user.is_active:
                inactive_user = self.user
                continue

            existing_user = self._resolve_existing_user(field, value)
            if not existing_user or not existing_user.check_password(password):
                continue

            self.user = existing_user
            if self.user.is_active:
                return attrs
            inactive_user = self.user

        if inactive_user is not None:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [self.error_messages["inactive_account"]],
                    "code": "inactive_account",
                },
                code="inactive_account",
            )

        self.fail("invalid_credentials")
