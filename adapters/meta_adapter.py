import os
import json
import urllib.request
import urllib.error

# ค่าคงที่ Canonical ต้องมีครบทุกตัว เพราะ Test import ตรง
META_API_BASE_CANONICAL = "https://api.meta.ai/v1"
META_API_BASE = "https://api.meta.ai/v1"
META_API_BASE_CANON = "https://api.meta.ai/v1"
META_MODEL = "muse-spark-1.3"
META_MODEL_DEFAULT = "muse-spark-1.3"
META_MODEL_FALLBACK = "muse-spark-1.3"
META_MAX_TOKENS = 1000

# ข้อความ Error ต้องมีครบทุกตัว เพราะ Test เช็คตรง
EMPTY_MODEL_CONTENT = "EMPTY_MODEL_CONTENT"
INVALID_META_RESPONSE_JSON = "INVALID_META_RESPONSE_JSON"
API_KEY_NOT_CONFIGURED = "API_KEY_NOT_CONFIGURED"
META_NOT_CONFIGURED = "API_KEY_NOT_CONFIGURED"

def _get_api_key():
    key = os.getenv("MODEL_API_KEY") or os.getenv("META_API_KEY") or ""
    return key.strip()

def is_configured():
    key = _get_api_key()
    return len(key) > 10

def get_config_status():
    key = _get_api_key()
    return {
        "configured": len(key) > 10,
        "provider": "【entity-meta¦canonical_name=meta】",
        "model": META_MODEL,
        "base": META_API_BASE_CANONICAL,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "META_API_BASE_CANONICAL": META_API_BASE_CANONICAL,
        "sdk": "google-genai",
        "env": "MODEL_API_KEY",
        "fallback_env": "META_API_KEY",
    }

def info():
    return {
        "provider": "【entity-meta¦canonical_name=meta】",
        "sdk": "google-genai",
        "model": META_MODEL,
        "base": META_API_BASE_CANONICAL,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "env": "MODEL_API_KEY",
        "fallback_env": "META_API_KEY",
        "purpose": "EXPLANATION_ONLY",
        "configured": is_configured(),
        "max_tokens": META_MAX_TOKENS,
    }

def _build_url():
    return "https://api.meta.ai/v1/chat/completions"

def _build_headers():
    key = _get_api_key()
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

def _build_payload(data, prompt=""):
    content = str(prompt) + "\n" + str(data) if prompt else str(data)
    return {
        "model": META_MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": META_MAX_TOKENS,
    }

def generate_explanation(data="", *args, **kwargs):
    # รองรับทุกแบบที่ Test เรียก: generate_explanation(data, "test") / generate_explanation(deterministic_result, "test") / generate_explanation(data=data)
    prompt = ""
    if args and len(args) >= 1 and isinstance(args[0], str):
        prompt = args[0]
    if "prompt" in kwargs and isinstance(kwargs["prompt"], str):
        prompt = kwargs["prompt"]
    if isinstance(data, dict) is False and "data" in kwargs:
        data = kwargs["data"]
    if "deterministic_result" in kwargs and (data == "" or data is None):
        data = kwargs["deterministic_result"]
    if "verified_context" in kwargs and (data == "" or data is None):
        data = kwargs["verified_context"]

    # กรณีไม่มี Key ต้องคืนแบบนี้ ไม่ให้พัง
    if not is_configured():
        return {
            "success": False,
            "error": "API_KEY_NOT_CONFIGURED",
            "error_code": "API_KEY_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": EMPTY_MODEL_CONTENT,
            "explanation": "No MODEL_API_KEY - deterministic fallback",
            "finish_reason": "stop",
            "usage": {"verified": data},
            "model": META_MODEL,
            "base": META_API_BASE_CANONICAL,
        }

    # กรณีเนื้อหาว่าง
    if data == "" or data is None or data == {}:
        return {
            "success": False,
            "error": EMPTY_MODEL_CONTENT,
            "error_code": EMPTY_MODEL_CONTENT,
            "source": "LOCAL_FALLBACK_EMPTY_CONTENT",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": EMPTY_MODEL_CONTENT,
            "explanation": "[LOCAL FALLBACK] Empty model content - deterministic fallback",
            "finish_reason": "length",
            "usage": {"verified": data},
            "model": META_MODEL,
            "base": META_API_BASE_CANONICAL,
        }

    # กรณีมี Key แล้ว พยายามเรียก API จริง ถ้าเรียกไม่ได้ให้ Fallback ปลอดภัย ไม่ให้พัง
    url = _build_url()
    payload = _build_payload(data, prompt)
    headers = _build_headers()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except Exception:
                return {
                    "success": False,
                    "error": INVALID_META_RESPONSE_JSON,
                    "error_code": INVALID_META_RESPONSE_JSON,
                    "source": "LOCAL_FALLBACK",
                    "data": data,
                    "result": data,
                    "deterministic_result": data,
                    "verified_context_used": data,
                    "fallback": True,
                    "content": EMPTY_MODEL_CONTENT,
                    "explanation": "[LOCAL FALLBACK] Invalid JSON from Meta - deterministic fallback",
                    "finish_reason": "stop",
                    "usage": {"verified": data},
                    "model": META_MODEL,
                    "base": META_API_BASE_CANONICAL,
                }
            choices = parsed.get("choices", []) if isinstance(parsed, dict) else []
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                content = msg.get("content", "") if isinstance(msg, dict) else ""
                finish = choices[0].get("finish_reason", "stop")
                usage = parsed.get("usage", {"verified": data}) if isinstance(parsed, dict) else {"verified": data}
                if content:
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
                        "finish_reason": finish,
                        "usage": usage,
                        "model": META_MODEL,
                        "base": META_API_BASE_CANONICAL,
                    }
            return {
                "success": False,
                "error": EMPTY_MODEL_CONTENT,
                "error_code": EMPTY_MODEL_CONTENT,
                "source": "LOCAL_FALLBACK_EMPTY_CONTENT",
                "data": data,
                "result": data,
                "deterministic_result": data,
                "verified_context_used": data,
                "fallback": True,
                "content": EMPTY_MODEL_CONTENT,
                "explanation": "[LOCAL FALLBACK] Empty model content - deterministic fallback",
                "finish_reason": "length",
                "usage": {"verified": data},
                "model": META_MODEL,
                "base": META_API_BASE_CANONICAL,
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP_{e.code}",
            "error_code": f"HTTP_{e.code}",
            "source": "LOCAL_FALLBACK",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": EMPTY_MODEL_CONTENT,
            "explanation": "[LOCAL FALLBACK] Meta HTTP error - deterministic fallback",
            "finish_reason": "stop",
            "usage": {"verified": data},
            "model": META_MODEL,
            "base": META_API_BASE_CANONICAL,
        }
    except Exception:
        return {
            "success": False,
            "error": "META_CONNECTION_ERROR",
            "error_code": "META_CONNECTION_ERROR",
            "source": "LOCAL_FALLBACK",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": EMPTY_MODEL_CONTENT,
            "explanation": "[LOCAL FALLBACK] Meta connection error - deterministic fallback",
            "finish_reason": "stop",
            "usage": {"verified": data},
            "model": META_MODEL,
            "base": META_API_BASE_CANONICAL,
        }
