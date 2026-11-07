import os
def is_configured():
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
def info():
    return {"provider": "gemini", "sdk": "google-genai", "model": "gemini-3.8-flash", "env": "GEMINI_API_KEY", "purpose": "EXPLANATION_ONLY", "configured": is_configured()}
