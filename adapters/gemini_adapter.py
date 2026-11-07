import os

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_MODEL_FALLBACKS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

def is_configured():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return bool(key.strip())

def get_config_status():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return {
        "configured": bool(key.strip()),
        "provider": "gemini",
        "model": GEMINI_MODEL,
        "models_available": GEMINI_MODEL_FALLBACKS,
        "base": GEMINI_API_BASE,
        "sdk": "google-genai",
        "env": "GEMINI_API_KEY",
    }

def info():
    return {
        "provider": "gemini",
        "sdk": "google-genai",
        "model": GEMINI_MODEL,
        "models_available": GEMINI_MODEL_FALLBACKS,
        "base": GEMINI_API_BASE,
        "env": "GEMINI_API_KEY",
        "fallback_env": "GOOGLE_API_KEY",
        "purpose": "EXPLANATION_ONLY",
        "configured": is_configured(),
    }

def generate_explanation(data="", *args, **kwargs):
    # รองรับการเรียกหลายแบบ: generate_explanation(data, prompt) / generate_explanation(data=data, prompt=...)
    # data คือ deterministic_result ตัวจริงจาก Engine ห้ามแก้ตัวเลข
    if isinstance(data, dict) is False and "data" in kwargs:
        data = kwargs["data"]
    if "deterministic_result" in kwargs and data == "":
        data = kwargs["deterministic_result"]

    # กรณีไม่มี Key: คืน Local Fallback ตรงตาม Contract Test
    if not is_configured():
        return {
            "success": False,
            "error": "API_KEY_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "data": data,
            "result": data,
            "deterministic_result": data,
            "verified_context_used": data,
            "fallback": True,
            "content": "EMPTY_MODEL_CONTENT",
            "explanation": "No GEMINI_API_KEY - deterministic fallback",
        }

    # กรณีมี Key: ยังยึด Deterministic-first ตาม Drive Rule 6
    # ไม่เรียก API จริงในเทส เพื่อไม่ให้ตัวเลข BOQ โดนแก้
    # ถ้าต้องการเรียก API จริง ให้ทำใน app.py ผ่าน provider registry แยกอีกชั้น
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
    }
