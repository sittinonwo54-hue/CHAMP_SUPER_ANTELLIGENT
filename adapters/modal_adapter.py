import os
def is_configured():
    return bool(os.getenv("MODAL_PROXY_TOKEN"))
def info():
    return {"provider": "modal", "model_family": "Muse Spark Open", "discovery": "GET /v1/models", "inference": "POST /v1/chat/completions", "source": "MODAL_MUSE_SPARK_OPEN", "env": "MODAL_PROXY_TOKEN", "purpose": "EXPLANATION_ONLY", "configured": is_configured()}
