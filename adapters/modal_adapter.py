import os
def is_configured():
    return bool(os.getenv("MODAL_PROXY_TOKEN"))
def info():
    return {"provider": "modal", "sdk": "google-genai", "model": "Muse Spark Open", "env": "MODAL_PROXY_TOKEN", "purpose": "EXPLANATION_ONLY", "configured": is_configured()}
def get_config_status():
    token = os.getenv("MODAL_PROXY_TOKEN") or ""
    return {"configured": bool(token), "model": "Muse Spark Open", "provider": "modal", "base": "https://api.modal.com/v1", "sdk": "google-genai"}
def generate_explanation(data="", *args, **kwargs):
    if not is_configured():
        return {"success": False, "error": "MODAL_NOT_CONFIGURED", "source": "LOCAL_FALLBACK", "data": data, "result": data, "deterministic_result": data}
    return {"success": True, "error": None, "source": "LOCAL_FALLBACK", "data": data, "result": data, "deterministic_result": data}
