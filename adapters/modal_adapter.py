"""CHAMP Modal / Muse Spark Open explanation adapter."""

import json
import os
import requests

MODAL_BASE_URL = "https://inference.us-west.modal.direct/v1"


def get_config_status():
    token = os.getenv("MODAL_PROXY_TOKEN", "")
    return {
        "configured": token.startswith("wk-") and ".ws-" in token,
        "provider": "modal",
        "model_family": "Muse Spark Open",
        "base": os.getenv("MODAL_BASE_URL", MODAL_BASE_URL),
        "purpose": "EXPLANATION_ONLY",
        "rule_6_compliance": True,
    }


def is_configured():
    return get_config_status()["configured"]


def _headers():
    return {
        "Authorization": "Bearer " + os.getenv("MODAL_PROXY_TOKEN", ""),
        "Content-Type": "application/json",
    }


def _base():
    return os.getenv("MODAL_BASE_URL", MODAL_BASE_URL).rstrip("/")


def _discover_muse_model():
    configured = os.getenv("MODAL_MODEL", "").strip()
    if configured and "muse" in configured.lower():
        return configured

    response = requests.get(
        _base() + "/models",
        headers=_headers(),
        timeout=60,
    )
    response.raise_for_status()

    for item in response.json().get("data", []):
        model_id = item.get("id", "")
        if "muse-spark" in model_id.lower():
            return model_id

    raise RuntimeError("MUSE_SPARK_MODEL_NOT_FOUND")


def generate_explanation(verified_result, prompt=None):
    if not is_configured():
        return {
            "success": False,
            "error": "MODAL_NOT_CONFIGURED",
            "explanation": "Verified deterministic result remains unchanged.",
            "verified_context_used": verified_result,
            "source": "LOCAL_FALLBACK",
        }

    model = _discover_muse_model()

    system_prompt = (
        "You are the CHAMP explanation layer. "
        "Explain ONLY the verified deterministic result supplied to you. "
        "Never invent, modify, estimate, or recalculate BOQ, cost, "
        "quantity, soil, foundation, plant, material, sustainability, "
        "or engineering values."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "instruction": prompt or "Explain the verified result.",
                        "verified_result": verified_result,
                    },
                    ensure_ascii=False,
                    default=str,
                ),
            },
        ],
    }

    try:
        response = requests.post(
            _base() + "/chat/completions",
            headers=_headers(),
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:
            return {
                "success": False,
                "error": "MODAL_API_" + str(response.status_code),
                "http_status": response.status_code,
                "explanation": "Verified deterministic result remains unchanged.",
                "verified_context_used": verified_result,
                "source": "MODAL_FAILED",
            }

        data = response.json()
        explanation = data["choices"][0]["message"]["content"]

        return {
            "success": True,
            "explanation": explanation,
            "verified_context_used": verified_result,
            "source": "MODAL_MUSE_SPARK_OPEN",
            "model": model,
            "http_status": 200,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": "MODAL_EXCEPTION",
            "detail": str(exc)[:500],
            "explanation": "Verified deterministic result remains unchanged.",
            "verified_context_used": verified_result,
            "source": "LOCAL_FALLBACK_EXCEPTION",
        }
