import os
def is_configured():
    return bool(os.getenv("MODEL_API_KEY") or os.getenv("META_API_KEY"))
def info():
    return {"provider": "meta", "base": "https://api.meta.ai/v1", "endpoint": "POST /v1/chat/completions", "model": "muse-spark-1.3", "env": "MODEL_API_KEY", "purpose": "EXPLANATION_ONLY", "configured": is_configured()}
