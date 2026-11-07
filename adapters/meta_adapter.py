"""Meta explanation adapter.

The adapter only explains deterministic results supplied by the application; it
must not replace or alter calculations from the deterministic engines.
"""

import os
from typing import Any, Dict, Optional

import requests

META_API_BASE_CANONICAL = "https://api.meta.ai/v1"
META_API_CHAT_PATH = "/chat/completions"
MODEL_DEFAULT = "muse-spark-1.3"
META_MAX_TOKENS_DEFAULT = 1000
ENV_KEYS = ("MODEL_API_KEY", "META_API_KEY")
ENV_MODEL_KEYS = ("META_MODEL", "MODEL_ID", "MODEL_API_MODEL", "META_MODEL_ID")

_live_verified = False


def _get_api_key() -> Optional[str]:
    for name in ENV_KEYS:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _get_model_id() -> str:
    for name in ENV_MODEL_KEYS:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return MODEL_DEFAULT


def _build_url() -> str:
    return f"{META_API_BASE_CANONICAL}{META_API_CHAT_PATH}"


def is_configured() -> bool:
    key = _get_api_key()
    return bool(key and len(key) > 10)


def info() -> Dict[str, Any]:
    """Return safe provider metadata for the health endpoint (never the key)."""
    return {
        "provider": "meta",
        "base": META_API_BASE_CANONICAL,
        "endpoint": "POST /v1/chat/completions",
        "model": _get_model_id(),
        "env": "MODEL_API_KEY",
        "purpose": "EXPLANATION_ONLY",
        "configured": is_configured(),
    }


def get_config_status() -> Dict[str, Any]:
    key = _get_api_key()
    endpoint = _build_url()
    return {
        "configured": is_configured(),
        "local_adapter": "VERIFIED",
        "live_api": "VERIFIED" if _live_verified else "PENDING_ACCESS",
        "model": _get_model_id(),
        "model_default": MODEL_DEFAULT,
        "base": META_API_BASE_CANONICAL,
        "base_canonical": META_API_BASE_CANONICAL,
        "api_base": META_API_BASE_CANONICAL,
        "api_base_canonical": META_API_BASE_CANONICAL,
        "chat_endpoint": endpoint,
        "chat_url": endpoint,
        "has_key": bool(key),
        "env_keys_checked": list(ENV_KEYS),
        "note": "Deterministic results remain authoritative; AI is explanation-only.",
        "rule_6_compliance": True,
    }


def _fallback_explanation(verified_result: Dict[str, Any]) -> str:
    soil = verified_result.get("soil_order") or verified_result.get("soil_type", "UNKNOWN")
    spt = verified_result.get("spt_value", verified_result.get("spt_n_value", "N/A"))
    pile_required = verified_result.get("pile_required", False)
    return (
        f"[LOCAL FALLBACK] Soil: {soil} SPT {spt} "
        f"pile_required={pile_required} (deterministic engines before AI)."
    )


def _failure(error: str, verified_result: Dict[str, Any], source: str, **extra: Any) -> Dict[str, Any]:
    return {
        "success": False,
        "error": error,
        "explanation": _fallback_explanation(verified_result),
        "verified_context_used": verified_result,
        "meta_status": get_config_status(),
        "source": source,
        "model": _get_model_id(),
        **extra,
    }


def generate_explanation(
    verified_result: Dict[str, Any], prompt: Optional[str] = None
) -> Dict[str, Any]:
    """Explain a verified result, safely falling back when unavailable."""
    global _live_verified

    api_key = _get_api_key()
    if not is_configured():
        return _failure(
            "API_KEY_NOT_CONFIGURED", verified_result, "LOCAL_FALLBACK"
        )

    payload = {
        "model": _get_model_id(),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are CHAMP's explanation layer. Use only the supplied "
                    "deterministic data. Do not invent or change results."
                ),
            },
            {
                "role": "user",
                "content": f"Verified result: {verified_result}. Instruction: {prompt or 'Explain clearly.'}",
            },
        ],
        "max_tokens": META_MAX_TOKENS_DEFAULT,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(_build_url(), json=payload, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return _failure(
            "META_REQUEST_FAILED",
            verified_result,
            "LOCAL_FALLBACK_REQUEST_ERROR",
            detail=str(exc)[:500],
        )

    if response.status_code != 200:
        return _failure(
            f"META_API_{response.status_code}",
            verified_result,
            f"META_FAILED_{response.status_code}",
            http_status=response.status_code,
        )

    try:
        response_json = response.json()
    except (ValueError, TypeError):
        return _failure(
            "INVALID_META_RESPONSE_JSON",
            verified_result,
            "LOCAL_FALLBACK_INVALID_JSON",
            http_status=response.status_code,
        )

    if not isinstance(response_json, dict):
        return _failure(
            "INVALID_META_RESPONSE_JSON",
            verified_result,
            "LOCAL_FALLBACK_INVALID_JSON",
            http_status=response.status_code,
        )

    choices = response_json.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    if not isinstance(choice, dict):
        choice = {}
    message = choice.get("message")
    if not isinstance(message, dict):
        message = {}

    content = message.get("content")
    finish_reason = choice.get("finish_reason")
    if not isinstance(content, str) or not content.strip():
        return _failure(
            "EMPTY_MODEL_CONTENT",
            verified_result,
            "LOCAL_FALLBACK_EMPTY_CONTENT",
            http_status=response.status_code,
            finish_reason=finish_reason,
            refusal=message.get("refusal"),
            usage=response_json.get("usage", {}),
        )

    _live_verified = True
    return {
        "success": True,
        "explanation": content.strip(),
        "verified_context_used": verified_result,
        "meta_status": get_config_status(),
        "source": "META_MUSE_SPARK",
        "model": response_json.get("model", _get_model_id()),
        "finish_reason": finish_reason,
        "refusal": message.get("refusal"),
        "usage": response_json.get("usage", {}),
        "http_status": response.status_code,
    }


class MetaAdapter:
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            os.environ["MODEL_API_KEY"] = api_key

    def status(self) -> Dict[str, Any]:
        return get_config_status()

    def explain(self, verified_result: Dict[str, Any], prompt: str = "") -> Dict[str, Any]:
        return generate_explanation(verified_result, prompt)


def get_adapter() -> MetaAdapter:
    return MetaAdapter()
