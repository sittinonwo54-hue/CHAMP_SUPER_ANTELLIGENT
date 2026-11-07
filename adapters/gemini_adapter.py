import os
def is_configured():
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
def info():
    return {"provider": "gemini", "sdk": "google-genai", "model": "gemini-3.8-flash", "env": "GEMINI_API_KEY", "purpose": "EXPLANATION_ONLY", "configured": is_configured()}
def get_config_status():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return {"configured": bool(key), "model": "gemini-3.8-flash", "provider": "gemini", "base": "https://generativelanguage.googleapis.com/v1beta", "sdk": "google-genai"}
def generate_explanation(data="", *args, **kwargs):
    if not is_configured():
        return {"success": False, "error": "API_KEY_NOT_CONFIGURED", "source": "LOCAL_FALLBACK", "data": data, "result": data, "deterministic_result": data}
    return {"success": True, "error": None, "source": "LOCAL_FALLBACK", "data": data, "result": data, "deterministic_result": data}
