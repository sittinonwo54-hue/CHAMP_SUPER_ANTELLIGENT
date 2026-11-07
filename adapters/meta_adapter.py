import os

import requests

META_API_BASE_CANONICAL = "https://api.meta.ai/v1"
META_API_BASE = "https://api.meta.ai/v1"
META_MODEL = "muse-spark-1.3"
META_MAX_TOKENS = 1000
EMPTY_MODEL_CONTENT = "EMPTY_MODEL_CONTENT"
INVALID_META_RESPONSE_JSON = "INVALID_META_RESPONSE_JSON"
API_KEY_NOT_CONFIGURED = "API_KEY_NOT_CONFIGURED"

def _get_api_key():
    key = os.getenv("MODEL_API_KEY") or os.getenv("META_API_KEY") or ""
    return key.strip()

def is_configured():
    return len(_get_api_key()) > 10

def get_config_status():
    configured = is_configured()
    return {
        "configured": configured,
        "provider": "【entity-meta¦canonical_name=Meta】",
        "model": META_MODEL,
        "base": META_API_BASE_CANONICAL,
        "api_base_canonical": META_API_BASE_CANONICAL,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "META_API_BASE_CANONICAL": META_API_BASE_CANONICAL,
        "chat_endpoint": _build_url(),
        "transport": "requests",
        "env": "MODEL_API_KEY",
        "fallback_env": "META_API_KEY",
    }

def info():
    return {
        "provider": "【entity-meta¦canonical_name=Meta】",
        "transport": "requests",
        "model": META_MODEL,
        "base": META_API_BASE_CANONICAL,
        "api_base_canonical": META_API_BASE_CANONICAL,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "META_API_BASE_CANONICAL": META_API_BASE_CANONICAL,
        "chat_endpoint": _build_url(),
        "env": "MODEL_API_KEY",
        "fallback_env": "META_API_KEY",
        "purpose": "EXPLANATION_ONLY",
        "configured": is_configured(),
        "max_tokens": META_MAX_TOKENS,
    }

def _build_url():
    return "https://api.meta.ai/v1/chat/completions"

def _build_headers():
    return {
        "Authorization": "Bearer " + _get_api_key(),
        "Content-Type": "application/json",
    }

def _build_payload(data, prompt=""):
    if prompt:
        content = str(prompt) + "\n" + str(data)
    else:
        content = str(data)
    return {
        "model": META_MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": META_MAX_TOKENS,
    }

def _fallback_result(data, error, source, explanation, finish_reason="stop"):
    return {
        "success": False,
        "error": error,
        "error_code": error,
        "source": source,
        "data": data,
        "result": data,
        "deterministic_result": data,
        "verified_context_used": data,
        "fallback": True,
        "content": EMPTY_MODEL_CONTENT,
        "explanation": explanation,
        "finish_reason": finish_reason,
        "usage": {"verified": data},
        "model": META_MODEL,
        "base": META_API_BASE_CANONICAL,
        "api_base_canonical": META_API_BASE_CANONICAL,
    }

def generate_explanation(data="", prompt="", *args, **kwargs):
    if args and len(args) >= 1 and isinstance(args[0], str):
        if not prompt:
            prompt = args[0]
    if isinstance(kwargs.get("prompt"), str):
        prompt = kwargs["prompt"]
    if "data" in kwargs and (data == "" or data is None):
        data = kwargs["data"]
    if (data == "" or data is None) and "deterministic_result" in kwargs:
        data = kwargs["deterministic_result"]
    if (data == "" or data is None) and "verified_context" in kwargs:
        data = kwargs["verified_context"]
    if (data == "" or data is None) and "verified_context_used" in kwargs:
        data = kwargs["verified_context_used"]
    if not is_configured():
        return _fallback_result(
            data,
            API_KEY_NOT_CONFIGURED,
            "LOCAL_FALLBACK",
            "No MODEL_API_KEY - deterministic fallback",
        )
    if data == "" or data is None or data == {}:
        return _fallback_result(
            data,
            EMPTY_MODEL_CONTENT,
            "LOCAL_FALLBACK_EMPTY_CONTENT",
            "[LOCAL FALLBACK] Empty model content - deterministic fallback",
            "length",
        )
    url = _build_url()
    payload = _build_payload(data, prompt)
    headers = _build_headers()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        status_code = getattr(response, "status_code", 200)
        if isinstance(status_code, int) and status_code >= 400:
            error = "HTTP_" + str(status_code)
            return _fallback_result(
                data,
                error,
                "LOCAL_FALLBACK",
                "[LOCAL FALLBACK] 【entity-Meta¦canonical_name=Meta】 HTTP error - deterministic fallback",
            )
        try:
            parsed = response.json()
        except Exception:
            return _fallback_result(
                data,
                INVALID_META_RESPONSE_JSON,
                "LOCAL_FALLBACK",
                "[LOCAL FALLBACK] Invalid JSON from 【entity-Meta¦canonical_name=Meta】 - deterministic fallback",
            )
        choices = parsed.get("choices", []) if isinstance(parsed, dict) else []
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message", {})
            if isinstance(message, dict):
                content = message.get("content", "")
            else:
                content = ""
            finish_reason = choices[0].get("finish_reason", "stop")
            if isinstance(parsed, dict):
                usage = parsed.get("usage", {"verified": data})
            else:
                usage = {"verified": data}
            if content is None or not isinstance(content, str) or content.strip() == "":
                return _fallback_result(
                    data,
                    EMPTY_MODEL_CONTENT,
                    "LOCAL_FALLBACK_EMPTY_CONTENT",
                    "[LOCAL FALLBACK] Empty model content - deterministic fallback",
                    "length",
                )
            return {
                "success": True,
                "error": None,
                "error_code": None,
                "source": "META_MUSE_SPARK",
                "data": data,
                "result": data,
                "deterministic_result": data,
                "verified_context_used": data,
                "fallback": False,
                "content": content,
                "explanation": content,
                "finish_reason": finish_reason,
                "usage": usage,
                "model": META_MODEL,
                "base": META_API_BASE_CANONICAL,
                "api_base_canonical": META_API_BASE_CANONICAL,
            }
        return _fallback_result(
            data,
            EMPTY_MODEL_CONTENT,
            "LOCAL_FALLBACK_EMPTY_CONTENT",
            "[LOCAL FALLBACK] Empty model content - deterministic fallback",
            "length",
        )
    except requests.RequestException as error:
        resp = getattr(error, "response", None)
        status_code = getattr(resp, "status_code", None) if resp is not None else None
        if status_code is not None:
            code = "HTTP_" + str(status_code)
            explanation = "[LOCAL FALLBACK] Meta HTTP error - deterministic fallback"
        else:
            code = "META_CONNECTION_ERROR"
            explanation = "[LOCAL FALLBACK] Meta connection error - deterministic fallback"
        return _fallback_result(data, code, "LOCAL_FALLBACK", explanation)
    except Exception:
        return _fallback_result(
            data,
            "META_CONNECTION_ERROR",
            "LOCAL_FALLBACK",
            "[LOCAL FALLBACK] Meta connection error - deterministic fallback",
        )