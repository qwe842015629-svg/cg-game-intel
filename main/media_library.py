import hashlib
import mimetypes
import os
import re
import uuid
from io import BytesIO
from typing import Any

from django.core.files.base import ContentFile
from django.db import transaction

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

from .models import MediaAsset


_ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif"}


def calculate_content_hash(payload: bytes) -> str:
    if not payload:
        return ""
    return hashlib.sha256(payload).hexdigest()


def _normalize_extension(file_name: str, content_type: str = "") -> str:
    ext = os.path.splitext(str(file_name or ""))[1].lower()
    if ext in _ALLOWED_IMAGE_EXTENSIONS:
        if ext == ".jpe":
            return ".jpg"
        return ext

    guessed = ""
    mime = str(content_type or "").split(";")[0].strip().lower()
    if mime:
        guessed = mimetypes.guess_extension(mime) or ""
    if guessed == ".jpe":
        guessed = ".jpg"
    if guessed in _ALLOWED_IMAGE_EXTENSIONS:
        return guessed
    return ".jpg"


def _safe_stem(value: str, default: str = "image") -> str:
    raw = os.path.splitext(os.path.basename(str(value or "").strip()))[0]
    cleaned = re.sub(r"[^\w\-]+", "-", raw, flags=re.ASCII).strip("-_.")
    if not cleaned:
        cleaned = default
    return cleaned[:100]


def _read_file_bytes(file_obj: Any) -> tuple[bytes, str]:
    if file_obj is None:
        return b"", ""

    source_name = str(
        getattr(file_obj, "name", "")
        or getattr(getattr(file_obj, "file", None), "name", "")
        or ""
    ).strip()

    previous_pos = None
    try:
        if hasattr(file_obj, "tell"):
            previous_pos = file_obj.tell()
    except Exception:
        previous_pos = None

    payload = b""
    try:
        if hasattr(file_obj, "open"):
            try:
                file_obj.open("rb")
            except TypeError:
                file_obj.open()
        payload = file_obj.read() or b""
    except Exception:
        payload = b""
    finally:
        try:
            if hasattr(file_obj, "seek"):
                if previous_pos is not None:
                    file_obj.seek(previous_pos)
                else:
                    file_obj.seek(0)
        except Exception:
            pass
        try:
            if hasattr(file_obj, "close"):
                file_obj.close()
        except Exception:
            pass

    if not isinstance(payload, (bytes, bytearray)):
        payload = bytes(payload or b"")
    return bytes(payload), source_name


def _build_thumbnail_content(payload: bytes, *, stem: str) -> ContentFile | None:
    if not payload or Image is None:
        return None
    try:
        image = Image.open(BytesIO(payload))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        thumb = image.copy()
        thumb.thumbnail((300, 300))
        thumb_io = BytesIO()
        thumb.save(thumb_io, format="JPEG", quality=85)
        thumb_name = f"thumb-{stem}-{uuid.uuid4().hex[:8]}.jpg"
        return ContentFile(thumb_io.getvalue(), name=thumb_name)
    except Exception:
        return None


def _build_unique_storage_name(*, requested_name: str, content_hash: str) -> str:
    ext = _normalize_extension(requested_name)
    stem = _safe_stem(requested_name, default="asset")
    return f"{stem}-{content_hash[:12]}-{uuid.uuid4().hex[:8]}{ext}"


def _build_unique_asset_name(
    *,
    requested_name: str,
    content_hash: str,
    exclude_id: int | None = None,
) -> str:
    ext = _normalize_extension(requested_name)
    stem = _safe_stem(requested_name, default="asset")
    base = f"{stem}-{content_hash[:10]}{ext}"
    candidate = base
    index = 2
    while MediaAsset.objects.filter(name=candidate).exclude(pk=exclude_id).exists():
        candidate = f"{stem}-{content_hash[:8]}-{index}{ext}"
        index += 1
    return candidate


@transaction.atomic
def upsert_media_asset(
    *,
    file_obj: Any,
    requested_name: str = "",
    category: str = "other",
    alt_text: str = "",
    create_thumbnail: bool = True,
) -> tuple[MediaAsset, bool]:
    payload, source_name = _read_file_bytes(file_obj)
    if not payload:
        raise ValueError("empty file payload")

    content_hash = calculate_content_hash(payload)
    if not content_hash:
        raise ValueError("unable to calculate content hash")

    existing = MediaAsset.objects.filter(content_hash=content_hash).order_by("id").first()
    if existing is not None:
        return existing, False

    incoming_name = str(requested_name or source_name or "asset.jpg").strip() or "asset.jpg"
    storage_name = _build_unique_storage_name(requested_name=incoming_name, content_hash=content_hash)
    asset_name = _build_unique_asset_name(requested_name=incoming_name, content_hash=content_hash)
    file_size_kb = max(1, int(len(payload) // 1024))

    instance = MediaAsset(
        name=asset_name,
        category=(str(category or "other").strip() or "other")[:50],
        alt_text=str(alt_text or "").strip()[:255],
        file_size=file_size_kb,
        content_hash=content_hash,
    )
    instance.file.save(storage_name, ContentFile(payload), save=False)

    if create_thumbnail:
        thumb = _build_thumbnail_content(payload, stem=_safe_stem(asset_name, default="thumb"))
        if thumb is not None:
            instance.thumbnail = thumb

    instance.save()
    return instance, True


@transaction.atomic
def dedupe_existing_media_assets(*, delete_duplicate_files: bool = True) -> dict[str, int]:
    assets = list(
        MediaAsset.objects.exclude(file__isnull=True)
        .exclude(file="")
        .order_by("id")
    )

    indexed = 0
    deleted = 0
    renamed = 0
    skipped = 0
    hash_to_keeper: dict[str, MediaAsset] = {}

    for asset in assets:
        payload, source_name = _read_file_bytes(asset.file)
        if not payload:
            skipped += 1
            continue
        digest = calculate_content_hash(payload)
        if not digest:
            skipped += 1
            continue
        indexed += 1

        keeper = hash_to_keeper.get(digest)
        if keeper is None:
            hash_to_keeper[digest] = asset
            changed = False
            if asset.content_hash != digest:
                asset.content_hash = digest
                changed = True
            desired_name = _build_unique_asset_name(
                requested_name=asset.name or source_name or "asset.jpg",
                content_hash=digest,
                exclude_id=asset.id,
            )
            if str(asset.name or "").strip() != desired_name:
                asset.name = desired_name
                changed = True
                renamed += 1
            if changed:
                asset.save(update_fields=["content_hash", "name", "updated_at"])
            continue

        if delete_duplicate_files:
            try:
                if asset.thumbnail:
                    asset.thumbnail.delete(save=False)
            except Exception:
                pass
            try:
                if asset.file:
                    asset.file.delete(save=False)
            except Exception:
                pass
            asset.delete()
            deleted += 1
        else:
            # content_hash is unique; keep duplicates untouched when retention is requested.
            skipped += 1

    return {
        "indexed": indexed,
        "deleted_duplicates": deleted,
        "renamed": renamed,
        "skipped": skipped,
    }
