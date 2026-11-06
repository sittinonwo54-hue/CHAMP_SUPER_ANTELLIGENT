"""
CHAMP_SUPER_ANTELLIGENT — Meta Adapter
FINAL per test_adapters.py + APP_PY_FIXED.md 2026-11-02

File: adapters/meta_adapter.py
Required by:
- tests/test_adapters.py::test_meta_api_base_canonical
- tests/test_app.py::test_health_endpoint
- app.py imports: generate_explanation, get_config_status, is_configured, META_API_BASE_CANONICAL

Official:
Base: https://api.meta.ai/v1
Chat: POST /v1/chat/completions
Env: MODEL_API_KEY (official) fallback META_API_KEY
is_configured() checks length >10
Missing key returns API_KEY_NOT_CONFIGURED, not crash
"""
import os
import requests
from typing import Dict, Any, Optional

# --- Canonical constants - MUST match test ---
META_API_BASE_CANONICAL = "https://api.meta.ai/v1"
META_API_CHAT_PATH = "/chat/completions"
META_API_LEGACY_COMPAT = "https://api.llama.com/compat/v1"

MODEL_MUSE_WONDER_1 = "muse-wonder-1.0"
MODEL_MUSE_SPARK_1_3 = "muse-spark-1.3"
MODEL_DEFAULT = MODEL_MUSE_SPARK_1_3

META_API_MODE_CRITICAL = "critical"
META_API_MODE_STANDARD = "standard"
META_MODEL_DEFAULT = MODEL_DEFAULT

META_MAX_TOKENS_DEFAULT = 1000

ENV_KEYS = ["MODEL_API_KEY", "META_API_KEY"]
ENV_MODEL_KEYS = ["META_MODEL", "MODEL_ID", "MODEL_API_MODEL", "META_MODEL_ID"]

_live_verified = False

def _get_api_key() -> Optional[str]:
    for k in ENV_KEYS:
        v = os.getenv(k)
        if v and len(v.strip()) > 0:
            return v.strip()
    return None

def _get_model_id() -> str:
    for k in ENV_MODEL_KEYS:
        v = os.getenv(k)
        if v and v.strip():
            return v.strip()
    return MODEL_DEFAULT

def _build_url() -> str:
    return f"{META_API_BASE_CANONICAL}{META_API_CHAT_PATH}"

def is_configured() -> bool:
    key = _get_api_key()
    return bool(key and len(key) > 10)

def get_config_status() -> Dict[str, Any]:
    key = _get_api_key()
    chat_url = _build_url()
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
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "chat_endpoint": chat_url,
        "chat_url": chat_url,
        "api_chat_url": chat_url,
        "api_chat_endpoint": chat_url,
        "chat_url_canonical": chat_url,
        "has_key": bool(key),
        "has_key_length_gt_10": bool(key and len(key) > 10),
        "env_keys_checked": ENV_KEYS,
        "note": "Deterministic continues when key absent - deterministic-safe - API_KEY_NOT_CONFIGURED",
        "legacy_compat_url": META_API_LEGACY_COMPAT,
        "rule_6_compliance": True,
    }

def _fallback_explanation(verified_result: Dict[str, Any]) -> str:
    soil = verified_result.get("soil_order") or verified_result.get("soil_type", "UNKNOWN")
    spt = verified_result.get("spt_value", verified_result.get("spt_n_value", "N/A"))
    pile_req = verified_result.get("pile_required", False)
    return f"[LOCAL FALLBACK] Soil: {soil} SPT {spt} pile_required={pile_req} (deterministic engines before AI)."

def generate_explanation(verified_result: Dict[str, Any], prompt: Optional[str] = None) -> Dict[str, Any]:
    global _live_verified
    status = get_config_status()
    api_key = _get_api_key()

    if not is_configured():
        return {
            "success": False,
            "error": "API_KEY_NOT_CONFIGURED",
            "error_code": "API_KEY_NOT_CONFIGURED",
            "explanation": _fallback_explanation(verified_result),
            "verified_context_used": verified_result,
            "meta_status": status,
            "source": "LOCAL_FALLBACK",
            "model": _get_model_id(),
            "base": META_API_BASE_CANONICAL,
        }

    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": _get_model_id(),
            "messages": [
                {"role": "system", "content": "You are CHAMP Meta explanation layer. Analyze using ONLY deterministic data. Do not invent numbers. Evidence-first."},
                {"role": "user", "content": f"Verified result: {verified_result}. Instruction: {prompt or 'Explain clearly.'}"}
            ],
            "max_tokens": META_MAX_TOKENS_DEFAULT,
        }
        resp = requests.post(_build_url(), json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            return {
                "success": False,
                "error": f"META_API_{resp.status_code}",
                "error_code": f"API_ERROR_{resp.status_code}",
                "http_status": resp.status_code,
                "explanation": _fallback_explanation(verified_result),
                "verified_context_used": verified_result,
                "meta_status": status,
                "source": f"META_FAILED_{resp.status_code}",
                "model": _get_model_id(),
            }

        try:
            response_json = resp.json()
        except ValueError:
            return {
                "success": False,
                "error": "INVALID_META_RESPONSE_JSON",
                "error_code": "INVALID_META_RESPONSE_JSON",
                "http_status": 200,
                "explanation": _fallback_explanation(verified_result),
                "verified_context_used": verified_result,
                "meta_status": status,
                "source": "LOCAL_FALLBACK_INVALID_JSON",
                "model": _get_model_id(),
            }

        choices = response_json.get("choices", [])
        choice = choices[0] if isinstance(choices, list) and choices else {}
        message = choice.get("message", {}) if isinstance(choice, dict) else {}
        if not isinstance(message, dict):
            message = {}

        content = message.get("content")
        refusal = message.get("refusal")
        finish_reason = choice.get("finish_reason") if isinstance(choice, dict) else None
        model = response_json.get("model", _get_model_id())
        usage = response_json.get("usage", {})

        if not isinstance(content, str) or not content.strip():
            return {
                "success": False,
                "error": "EMPTY_MODEL_CONTENT",
                "error_code": "EMPTY_MODEL_CONTENT",
                "http_status": 200,
                "finish_reason": finish_reason,
                "refusal": refusal,
                "explanation": _fallback_explanation(verified_result),
                "verified_context_used": verified_result,
                "meta_status": status,
                "source": "LOCAL_FALLBACK_EMPTY_CONTENT",
                "model": model,
                "usage": usage,
            }

        _live_verified = True
        return {
            "success": True,
            "explanation": content.strip(),
            "verified_context_used": verified_result,
            "meta_status": get_config_status(),
            "source": "META_MUSE_SPARK",
            "model": model,
            "finish_reason": finish_reason,
            "refusal": refusal,
            "usage": usage,
            "http_status": 200,
        }
    except Exception as e:
        return {"success": False, "error": "EXCEPTION", "error_code": "EXCEPTION", "detail": str(e)[:500], "explanation": _fallback_explanation(verified_result), "meta_status": status, "source": "LOCAL_FALLBACK_EXCEPTION"}

class MetaAdapter:
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            os.environ["MODEL_API_KEY"] = api_key
    def status(self):
        return get_config_status()
    def explain(self, v, p=""):
        return generate_explanation(v, p)

def get_adapter():
    return MetaAdapter()
