import hashlib
import hmac
import time

from django.conf import settings
from django.core.cache import cache


def get_client_ip(request) -> str:
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _ops_allowed_clients() -> list[str]:
    clients = getattr(settings, "OPS_GATEWAY_ALLOWED_CLIENTS", []) or []
    return [str(item).strip() for item in clients if str(item).strip()]


def _ops_hmac_secret() -> str:
    return str(getattr(settings, "OPS_GATEWAY_HMAC_SECRET", "") or "").strip()


def _ops_tolerance_seconds() -> int:
    try:
        return max(30, int(getattr(settings, "OPS_GATEWAY_TIMESTAMP_TOLERANCE", 300)))
    except Exception:
        return 300


def verify_hmac_signature(request) -> tuple[bool, str, str]:
    """
    Verify request signature.

    Canonical string:
    METHOD \\n PATH \\n TIMESTAMP \\n NONCE \\n SHA256(body)
    """
    secret = _ops_hmac_secret()
    if not secret:
        return False, "", "OPS_GATEWAY_HMAC_SECRET 未配置"

    client_id = str(request.headers.get("X-Client-Id", "")).strip()
    timestamp = str(request.headers.get("X-Timestamp", "")).strip()
    nonce = str(request.headers.get("X-Nonce", "")).strip()
    signature = str(request.headers.get("X-Signature", "")).strip()

    if not client_id or not timestamp or not nonce or not signature:
        return False, client_id, "缺少签名请求头"

    allowed_clients = _ops_allowed_clients()
    if allowed_clients and client_id not in allowed_clients:
        return False, client_id, "client_id 不在白名单"

    try:
        ts = int(timestamp)
    except Exception:
        return False, client_id, "X-Timestamp 格式错误"

    now = int(time.time())
    tolerance = _ops_tolerance_seconds()
    if abs(now - ts) > tolerance:
        return False, client_id, "签名时间戳过期"

    nonce_cache_key = f"ops_nonce:{client_id}:{nonce}"
    if not cache.add(nonce_cache_key, 1, timeout=tolerance):
        return False, client_id, "重复 nonce"

    body = request.body or b""
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = "\n".join(
        [
            request.method.upper(),
            request.path,
            timestamp,
            nonce,
            body_hash,
        ]
    )
    expected = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False, client_id, "签名校验失败"

    return True, client_id, ""

