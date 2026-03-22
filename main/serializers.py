from rest_framework import serializers

from game_recharge.i18n_utils import localize_text, normalize_locale_code, resolve_request_locale

from .models import (
    Banner,
    HomeLayout,
    SiteConfig,
    MediaAsset,
    NovelDraft,
    NovelWork,
    PlazaPost,
    PlazaComment,
)


PLAZA_BLOCKED_TERMS = [
    "porn",
    "nsfw",
    "nude",
    "hentai",
    "sex",
    "gambling",
    "casino",
    "betting",
    "drug",
    "cocaine",
    "heroin",
    "meth",
    "terror",
    "explosive",
    "gun trafficking",
    "human trafficking",
    "money laundering",
    "色情",
    "淫秽",
    "裸聊",
    "约炮",
    "嫖娼",
    "卖淫",
    "赌博",
    "赌资",
    "博彩",
    "彩票套利",
    "代开赌场",
    "毒品",
    "吸毒",
    "贩毒",
    "制毒",
    "枪支交易",
    "爆炸物",
    "恐怖袭击",
    "教唆犯罪",
    "诈骗",
    "洗钱",
    "人口贩卖",
    "黄赌毒",
]


def _build_image_url(request, image_field, updated_at=None) -> str:
    if not image_field:
        return ""

    url = image_field.url
    if request is not None:
        try:
            url = request.build_absolute_uri(url)
        except Exception:
            pass

    # Use updated_at as a cache-busting version so image replacement is reflected immediately.
    if updated_at:
        version = int(updated_at.timestamp())
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}v={version}"

    return url


def _validate_plaza_text(text: str, field_name: str = "content") -> str:
    value = str(text or "").strip()
    lowered = value.lower()
    for term in PLAZA_BLOCKED_TERMS:
        if term.lower() in lowered:
            raise serializers.ValidationError(f"{field_name} contains prohibited content ({term})")
    return value


def _resolve_serializer_locale(context: dict) -> str:
    request = context.get("request") if isinstance(context, dict) else None
    return resolve_request_locale(request)


def _is_empty_i18n_value(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    return False


def _locale_aliases(locale: str) -> list[str]:
    normalized = normalize_locale_code(locale)
    aliases = [normalized, normalized.lower(), normalized.replace("-", "_"), normalized.lower().replace("-", "_")]

    if normalized == "zh-CN":
        aliases.extend(["zh", "zh-cn", "zh_cn", "zh-hans", "zh_hans"])
    elif normalized == "zh-TW":
        aliases.extend(["zh", "zh-tw", "zh_tw", "zh-hk", "zh_hk", "zh-hant", "zh_hant"])
    elif normalized == "en":
        aliases.extend(["en-us", "en_us", "en-gb", "en_gb"])

    base = normalized.split("-", 1)[0].lower()
    aliases.append(base)
    deduped: list[str] = []
    for alias in aliases:
        item = str(alias or "").strip()
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _pick_i18n_value(i18n_map, locale: str):
    if not isinstance(i18n_map, dict) or not i18n_map:
        return None

    normalized_pairs = []
    for key, value in i18n_map.items():
        key_text = str(key or "").strip()
        if not key_text:
            continue
        normalized_pairs.append((key_text, value))
        normalized_pairs.append((key_text.lower(), value))
        normalized_pairs.append((key_text.replace("_", "-").lower(), value))

    for alias in _locale_aliases(locale):
        for key, value in normalized_pairs:
            if key == alias and not _is_empty_i18n_value(value):
                return value

    for fallback_locale in ("en", "zh-CN"):
        for alias in _locale_aliases(fallback_locale):
            for key, value in normalized_pairs:
                if key == alias and not _is_empty_i18n_value(value):
                    return value

    return None


def _localize_json_value(default_value, i18n_map, locale: str):
    localized = _pick_i18n_value(i18n_map, locale)
    if localized is None:
        return default_value
    return localized


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField()
    file = serializers.ImageField(write_only=True)

    class Meta:
        model = MediaAsset
        fields = [
            "id",
            "name",
            "file",
            "url",
            "thumbnail_url",
            "category",
            "alt_text",
            "file_size",
            "content_hash",
            "created_at",
        ]
        read_only_fields = ["file_size", "content_hash", "created_at"]


class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = [
            "site_name",
            "site_logo",
            "favicon",
            "seo_keywords",
            "seo_description",
            "primary_color",
            "secondary_color",
            "contact_email",
            "contact_phone",
            "is_maintenance_mode",
        ]

    def to_representation(self, instance):
        return {
            "siteName": instance.site_name,
            "siteLogo": instance.site_logo.url if instance.site_logo else "",
            "favicon": instance.favicon.url if instance.favicon else "",
            "seoKeywords": instance.seo_keywords,
            "seoDescription": instance.seo_description,
            "primaryColor": instance.primary_color,
            "secondaryColor": instance.secondary_color,
            "contactEmail": instance.contact_email,
            "contactPhone": instance.contact_phone,
            "isMaintenanceMode": instance.is_maintenance_mode,
        }


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id",
            "title",
            "description",
            "badge",
            "image",
            "primary_button_text",
            "primary_button_link",
            "secondary_button_text",
            "secondary_button_link",
            "sort_order",
            "view_count",
            "click_count",
        ]

    def to_representation(self, instance):
        instance.increase_view_count()
        request = self.context.get("request")
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        return {
            "id": instance.id,
            "title": localize_text(instance.title, getattr(instance, "title_i18n", {}), locale),
            "description": localize_text(
                instance.description, getattr(instance, "description_i18n", {}), locale
            ),
            "badge": localize_text(instance.badge, getattr(instance, "badge_i18n", {}), locale),
            "image": _build_image_url(request, instance.image, instance.updated_at),
            "primaryButton": localize_text(
                instance.primary_button_text,
                getattr(instance, "primary_button_text_i18n", {}),
                locale,
            ),
            "secondaryButton": localize_text(
                instance.secondary_button_text,
                getattr(instance, "secondary_button_text_i18n", {}),
                locale,
            ),
            "primaryLink": instance.primary_button_link,
            "secondaryLink": instance.secondary_button_link,
        }


class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["id", "title", "image", "badge", "sort_order"]

    def to_representation(self, instance):
        request = self.context.get("request")
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        return {
            "id": instance.id,
            "title": localize_text(instance.title, getattr(instance, "title_i18n", {}), locale),
            "description": localize_text(
                instance.description, getattr(instance, "description_i18n", {}), locale
            ),
            "badge": localize_text(instance.badge, getattr(instance, "badge_i18n", {}), locale),
            "image": _build_image_url(request, instance.image, instance.updated_at),
            "primaryButton": localize_text(
                instance.primary_button_text,
                getattr(instance, "primary_button_text_i18n", {}),
                locale,
            ),
            "secondaryButton": localize_text(
                instance.secondary_button_text,
                getattr(instance, "secondary_button_text_i18n", {}),
                locale,
            ),
            "primaryLink": instance.primary_button_link,
            "secondaryLink": instance.secondary_button_link,
        }


class HomeLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeLayout
        fields = ["id", "section_key", "section_name", "is_enabled", "sort_order", "config", "view_count"]

    def to_representation(self, instance):
        locale = _resolve_serializer_locale(getattr(self, "context", {}))
        localized_config = _localize_json_value(
            instance.config or {},
            getattr(instance, "config_i18n", {}),
            locale,
        )
        if not isinstance(localized_config, dict):
            localized_config = instance.config or {}

        return {
            "id": instance.id,
            "sectionKey": instance.section_key,
            "section_key": instance.section_key,
            "sectionName": localize_text(
                instance.section_name, getattr(instance, "section_name_i18n", {}), locale
            ),
            "isEnabled": instance.is_enabled,
            "sortOrder": instance.sort_order,
            "config": localized_config,
            "viewCount": instance.view_count,
        }


class NovelDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelDraft
        fields = [
            "id",
            "owner_key",
            "client_id",
            "title",
            "state",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_key", "created_at", "updated_at"]

    def validate_state(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("state must be a JSON object")
        return value

    def validate_client_id(self, value):
        return str(value or "").strip()[:64]


class NovelWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelWork
        fields = [
            "id",
            "owner_key",
            "client_id",
            "title",
            "summary",
            "plan",
            "chapters",
            "cover_image",
            "character_images",
            "chapter_images",
            "extra_meta",
            "visibility",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_key", "created_at", "updated_at"]

    def validate_client_id(self, value):
        return str(value or "").strip()[:64]

    def validate_plan(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("plan must be a JSON object")
        return value

    def validate_chapters(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("chapters must be a JSON array")
        return value

    def validate_character_images(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("character_images must be a JSON array")
        return value

    def validate_chapter_images(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("chapter_images must be a JSON array")
        return value

    def validate_extra_meta(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("extra_meta must be a JSON object")
        return value


class PlazaCommentSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = PlazaComment
        fields = [
            "id",
            "post",
            "owner_key",
            "author_id",
            "author_name",
            "author_avatar",
            "content",
            "created_at",
            "updated_at",
            "is_owner",
        ]
        read_only_fields = ["id", "post", "owner_key", "author_id", "created_at", "updated_at", "is_owner"]

    def get_author_id(self, obj):
        if obj.user_id:
            return int(obj.user_id)

        owner_key = str(obj.owner_key or "")
        if owner_key.startswith("user:"):
            raw = owner_key.split(":", 1)[-1]
            if raw.isdigit():
                return int(raw)
        return None

    def get_is_owner(self, obj):
        owner_key = str(self.context.get("owner_key") or "")
        return bool(owner_key and owner_key == obj.owner_key)

    def validate_content(self, value):
        text = _validate_plaza_text(value, "comment")
        if not text:
            raise serializers.ValidationError("comment cannot be empty")
        return text[:500]


class PlazaPostSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = PlazaPost
        fields = [
            "id",
            "owner_key",
            "author_id",
            "author_name",
            "author_avatar",
            "content",
            "post_type",
            "source_ref",
            "source_data",
            "visibility",
            "like_count",
            "comment_count",
            "comments",
            "liked_by_me",
            "is_owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner_key",
            "author_id",
            "like_count",
            "comment_count",
            "comments",
            "liked_by_me",
            "is_owner",
            "created_at",
            "updated_at",
        ]

    def get_author_id(self, obj):
        if obj.user_id:
            return int(obj.user_id)

        owner_key = str(obj.owner_key or "")
        if owner_key.startswith("user:"):
            raw = owner_key.split(":", 1)[-1]
            if raw.isdigit():
                return int(raw)
        return None

    def get_comments(self, obj):
        request = self.context.get("request")
        include_comments = str(getattr(request, "query_params", {}).get("include_comments", "1")).lower()
        if include_comments in {"0", "false", "no"}:
            return []
        queryset = obj.comments.all().order_by("created_at")[:80]
        serializer = PlazaCommentSerializer(queryset, many=True, context=self.context)
        return serializer.data

    def get_liked_by_me(self, obj):
        owner_key = str(self.context.get("owner_key") or "")
        if not owner_key:
            return False
        return obj.likes.filter(owner_key=owner_key).exists()

    def get_is_owner(self, obj):
        owner_key = str(self.context.get("owner_key") or "")
        return bool(owner_key and owner_key == obj.owner_key)

    def validate_post_type(self, value):
        if value not in dict(PlazaPost.POST_TYPE_CHOICES):
            raise serializers.ValidationError("post_type is invalid")
        return value

    def validate_content(self, value):
        text = _validate_plaza_text(value, "content")
        return text[:1200]

    def validate_source_ref(self, value):
        return str(value or "").strip()[:128]

    def validate_source_data(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("source_data must be a JSON object")

        compact = str(value)
        _validate_plaza_text(compact, "source_data")
        return value
