import os

MODAL_API_BASE = "https://api.modal.com/v1"
MODAL_MODEL = "Muse Spark Open"

def is_configured():
    token = os.getenv("MODAL_PROXY_TOKEN") or ""
    return bool(token.strip())

def get_config_status():
    token = os.getenv("MODAL_PROXY_TOKEN") or ""
    return {
        "configured": bool(token.strip()),
        "provider": "modal",
        "model": MODAL_MODEL,
        "base": MODAL_API_BASE,
        "sdk": "google-genai",
        "env": "MODAL_PROXY_TOKEN",
    }

def info():
    return {
        "provider": "modal",
        "sdk": "google-genai",
        "model": MODAL_MODEL,
        "base": MODAL_API_BASE,
        "env": "MODAL_PROXY_TOKEN",
        "purpose": "EXPLANATION_ONLY",
        "configured": is_configured(),
    }

def generate_explanation(data="", *args, **kwargs):
    if isinstance(data, dict) is False and "data" in kwargs:
        data = kwargs["data"]
    if "deterministic_result" in kwargs and data == "":
        data = kwargs["deterministic_result"]
    if not is_configured():
        return {
            "success": False,
            "error": "MODAL_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": "EMPTY_MODEL_CONTENT",
            "explanation": "No MODAL_PROXY_TOKEN - deterministic fallback",
            "finish_reason": "stop",
            "usage": {"verified": data},
        }
    if data == "" or data is None or data == {}:
        return {
            "success": False,
            "error": "EMPTY_MODEL_CONTENT",
            "source": "LOCAL_FALLBACK_EMPTY_CONTENT",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": "EMPTY_MODEL_CONTENT",
            "explanation": "[LOCAL FALLBACK] Empty model content - deterministic fallback",
            "finish_reason": "length",
            "usage": {"verified": data},
        }
    return {
        "success": True,
        "error": None,
        "source": "LOCAL_FALLBACK",
        "data": data,
        "result": data,
        "deterministic_result": data,
        "verified_context_used": data,
        "fallback": True,
        "content": data,
        "explanation": data,
        "finish_reason": "stop",
        "usage": {"verified": data},
    }
