"""
app.py - CHAMP_SUPER_ANTELLIGENT - CANONICAL RUNTIME

Pipeline:
USER INPUT
  |
  v
VALIDATION (utils/validation.py - DATA_GATE #4231)
  |
  v
DETERMINISTIC DOMAIN ENGINE (6 engines)
  |
  v
VERIFIED BOQ / SOIL / SITE RESULT
  |
  v
AI PROVIDER (Meta OR Gemini OR Modal) - EXPLANATION ONLY
  |
  v
STRUCTURED RESPONSE
  |
  v
AUDIT LOG (utils/audit.py)

Core API endpoints:
GET  /
GET  /api/health
POST /api/boq/calculate
POST /api/analyze-landscape
GET  /api/audit/logs
POST /api/soil/classify
POST /api/foundation/design

Security and evidence rules:
- No hardcoded secrets
- Provider credentials come from environment variables only
- Missing provider keys do not terminate deterministic processing
- DATA_GATE #4231 requires SPT for Vertisols
- Deterministic results are generated before the AI call
- AI providers explain verified results only
- Unknown providers are rejected
- Audit events record the provider actually selected
"""

import os
import sys
import traceback
from typing import Any, Callable, Dict, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS


# ---------------------------------------------------------------------------
# Local import path
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

from utils.validation import validate_landscape_input
from utils.audit import audit_log, get_audit_logs


# ---------------------------------------------------------------------------
# Deterministic engines
# ---------------------------------------------------------------------------

from engines.boq_engine import calculate_boq
from engines.soil_engine import classify_soil
from engines.foundation_engine import design_foundation
from engines.plant_engine import select_plants
from engines.material_engine import get_material_palette
from engines.leed_engine import calculate_leed


# ---------------------------------------------------------------------------
# AI provider adapters
# ---------------------------------------------------------------------------

from adapters.meta_adapter import (
    META_API_BASE_CANONICAL,
    generate_explanation as meta_explain,
    get_config_status as meta_config,
    is_configured as meta_configured,
)

from adapters.gemini_adapter import (
    generate_explanation as gemini_explain,
    get_config_status as gemini_config,
    is_configured as gemini_configured,
)

from adapters.modal_adapter import (
    generate_explanation as modal_explain,
    get_config_status as modal_config,
    is_configured as modal_configured,
)


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# System identity
# ---------------------------------------------------------------------------

SYSTEM_NAME = "CHAMP_SUPER_ANTELLIGENT"
VERSION = "1.0.0-hackathon"
TAGLINE = "Architecture Meets Nature Enhanced by AI"

SUPPORTED_PROVIDERS = ("meta", "gemini", "modal")

AIProviderFunction = Callable[
    [Dict[str, Any], str],
    Dict[str, Any],
]


# ---------------------------------------------------------------------------
# Common response helpers
# ---------------------------------------------------------------------------

def error_response(
    error: str,
    status_code: int,
    message: str,
    **extra: Any,
):
    """
    Return a controlled API error without exposing an internal traceback.
    """

    payload: Dict[str, Any] = {
        "success": False,
        "system": SYSTEM_NAME,
        "error": error,
        "message": message,
    }

    payload.update(extra)

    return jsonify(payload), status_code


def normalize_provider(raw_provider: Any) -> str:
    """
    Normalize the provider field without silently routing an invalid value.
    """

    if raw_provider is None:
        return "meta"

    if not isinstance(raw_provider, str):
        raise ValueError("Provider must be a string")

    provider = raw_provider.strip().lower()

    if not provider:
        return "meta"

    return provider


def provider_registry() -> Dict[str, AIProviderFunction]:
    """
    Explicit provider registry.

    This prevents provider=modal or an unknown provider from falling through
    to Meta while the response reports a different provider.
    """

    return {
        "meta": meta_explain,
        "gemini": gemini_explain,
        "modal": modal_explain,
    }


def execute_ai_provider(
    provider: str,
    deterministic_result: Dict[str, Any],
    user_prompt: str,
) -> Tuple[Dict[str, Any], str]:
    """
    Execute only the selected provider.

    Provider failures do not modify or recalculate deterministic results.
    """

    providers = provider_registry()

    if provider not in providers:
        raise ValueError(
            "Unsupported provider. Supported providers: "
            + ", ".join(SUPPORTED_PROVIDERS)
        )

    provider_function = providers[provider]

    try:
        result = provider_function(
            deterministic_result,
            user_prompt,
        )

        if not isinstance(result, dict):
            return {
                "success": False,
                "error": "INVALID_PROVIDER_RESPONSE",
                "error_code": "INVALID_PROVIDER_RESPONSE",
                "explanation": (
                    "Verified deterministic result remains unchanged."
                ),
                "verified_context_used": deterministic_result,
                "source": "LOCAL_FALLBACK_INVALID_RESPONSE",
            }, provider

        return result, provider

    except Exception as exc:
        audit_log(
            "AI_PROVIDER_EXCEPTION",
            {
                "provider": provider,
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            },
            success=False,
        )

        return {
            "success": False,
            "error": "AI_PROVIDER_EXCEPTION",
            "error_code": "AI_PROVIDER_EXCEPTION",
            "detail": str(exc)[:500],
            "explanation": (
                "Verified deterministic result remains unchanged."
            ),
            "verified_context_used": deterministic_result,
            "source": "LOCAL_FALLBACK_PROVIDER_EXCEPTION",
        }, provider


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "system": SYSTEM_NAME,
        "version": VERSION,
        "tagline": TAGLINE,
        "architecture": (
            "USER INPUT -> VALIDATION (DATA_GATE #4231) -> "
            "DETERMINISTIC DOMAIN ENGINE (6 engines) -> "
            "VERIFIED RESULT -> AI EXPLANATION ONLY -> RESPONSE -> AUDIT"
        ),
        "deterministic_engines": [
            "BOQ_ENGINE BaseRate 741",
            "SOIL_TAXONOMY 12 USDA Orders",
            "FOUNDATION_SOP Pile D30",
            "PLANT_KNOWLEDGE limited",
            "MATERIAL_PALETTE Thai 2024-2025",
            "LEED_V5 110pts",
        ],
        "ai_adapters": [
            "Meta",
            "Gemini google-genai",
            "Modal Muse Spark Open",
        ],
        "supported_providers": list(SUPPORTED_PROVIDERS),
        "endpoints": [
            "/",
            "/api/health",
            "/api/boq/calculate",
            "/api/analyze-landscape",
            "/api/audit/logs",
            "/api/soil/classify",
            "/api/foundation/design",
        ],
        "evidence": (
            "Evidence > Claims - Repair > Rebuild - "
            "One CHAMP > Many Versions"
        ),
        "rule_6_compliance": (
            "LLM must not invent BOQ values. "
            "Deterministic results are built before the AI call."
        ),
        "reality_check": {
            "deterministic_engines": 6,
            "ai_adapters_wired": 3,
            "plant_knowledge": "PARTIAL",
            "material_palette": "PARTIAL",
            "leed_v5": "PARTIAL",
        },
    })


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """
    Configuration health check.

    This endpoint checks local adapter configuration. It does not claim that
    an external provider is live unless the adapter reports that evidence.
    """

    try:
        meta_status = meta_config()
        gemini_status = gemini_config()
        modal_status = modal_config()

        return jsonify({
            "status": "healthy",
            "system": SYSTEM_NAME,
            "version": VERSION,
            "supported_providers": list(SUPPORTED_PROVIDERS),

            "meta_api_base_canonical": META_API_BASE_CANONICAL,
            "meta_config": meta_status,
            "meta_configured": meta_configured(),

            "gemini_sdk": "google-genai",
            "gemini_config": gemini_status,
            "gemini_configured": gemini_configured(),

            "modal_config": modal_status,
            "modal_configured": modal_configured(),

            "rule_6_compliance": (
                "Deterministic result before AI explanation"
            ),
            "data_gate_4231": (
                "SPT mandatory for Vertisols per validation.py"
            ),

            "deterministic_engines": {
                "boq_engine": "CODE READY",
                "soil_taxonomy": "CODE READY",
                "foundation_sop": "CODE READY",
                "plant_knowledge": "PARTIAL",
                "material_palette": "PARTIAL",
                "leed_v5": "PARTIAL",
            },

            "security": {
                "no_hardcoded_secrets": True,
                "credentials_source": "ENVIRONMENT_VARIABLES",
                "audit_log": "/tmp/champ_audit.log",
                "rate_limiting": "NOT_IMPLEMENTED",
                "api_authentication": "NOT_IMPLEMENTED",
                "audit_endpoint_authentication": "NOT_IMPLEMENTED",
            },

            "reality": {
                "agents_135": "DOCUMENTATION_ONLY",
                "subsystems_15_on_off": "DOCUMENTATION_ONLY",
                "plant_500": "DOCUMENTATION_ONLY",
                "projects_100": "DOCUMENTATION_ONLY",
                "vector_db_384_dim": "DOCUMENTATION_ONLY",
            },
        })

    except Exception as exc:
        audit_log(
            "HEALTH_CHECK_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            },
            success=False,
        )

        return error_response(
            error="HEALTH_CHECK_ERROR",
            status_code=500,
            message="Health configuration check failed",
        )


# ---------------------------------------------------------------------------
# BOQ
# ---------------------------------------------------------------------------

@app.route("/api/boq/calculate", methods=["POST"])
def boq_calculate():
    data: Dict[str, Any] = {}

    try:
        data = request.get_json(silent=True) or {}

        if not isinstance(data, dict):
            return error_response(
                error="INVALID_JSON_BODY",
                status_code=400,
                message="JSON body must be an object",
            )

        valid, normalized, errors = validate_landscape_input(data)

        if not valid:
            has_data_gate = any(
                "DATA_GATE #4231" in error
                for error in errors
            )

            audit_log(
                "BOQ_CALCULATE_VALIDATION_FAIL",
                {
                    "input": data,
                    "errors": errors,
                    "data_gate_4231": has_data_gate,
                },
                success=False,
            )

            status_code = 422 if has_data_gate else 400

            return jsonify({
                "success": False,
                "system": SYSTEM_NAME,
                "error": "VALIDATION_FAILED",
                "data_gate": (
                    "DATA_GATE #4231"
                    if has_data_gate
                    else "GENERAL_VALIDATION"
                ),
                "errors": errors,
                "normalized": normalized,
                "evidence": (
                    "SPT is mandatory for Vertisols. "
                    "No SPT, no deterministic build result."
                ),
            }), status_code

        boq_result = calculate_boq(
            area=normalized["area"],
            soil_type=normalized["soil_type"],
            slope_percent=normalized["slope_percent"],
            access_type=normalized["access_type"],
            spt=normalized.get("spt"),
            pile_count=normalized.get("pile_count", 24),
        )

        audit_log(
            "BOQ_CALCULATE_SUCCESS",
            {
                "area": normalized["area"],
                "soil": normalized["soil_type"],
                "grand_total": boq_result["grand_total"],
            },
            success=True,
        )

        return jsonify({
            "success": True,
            "system": SYSTEM_NAME,
            "engine": "BOQ_ENGINE",
            "input_normalized": normalized,
            "boq": boq_result,
            "validation": {
                "valid": valid,
                "errors": errors,
            },
            "evidence_status": {
                "base_rate_validation_88_1": "CODE_READY",
                "pj0014_calibration": "NOT_VERIFIED",
                "double_count_risk": "REQUIRES_REVIEW",
            },
        })

    except Exception as exc:
        audit_log(
            "BOQ_CALCULATE_ENGINE_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
                "input": data,
                "trace": traceback.format_exc()[:1000],
            },
            success=False,
        )

        return error_response(
            error="ENGINE_ERROR",
            status_code=500,
            message="BOQ calculation failed",
        )


# ---------------------------------------------------------------------------
# Full landscape analysis
# ---------------------------------------------------------------------------

@app.route("/api/analyze-landscape", methods=["POST"])
def analyze_landscape():
    """
    Full deterministic-first pipeline.

    The AI provider is allowed to explain the deterministic result only.
    The AI provider must not replace or recalculate BOQ/domain values.
    """

    data: Dict[str, Any] = {}

    try:
        data = request.get_json(silent=True) or {}

        if not isinstance(data, dict):
            return error_response(
                error="INVALID_JSON_BODY",
                status_code=400,
                message="JSON body must be an object",
            )

        user_prompt_raw = data.get(
            "prompt",
            data.get("query", "Analyze landscape project"),
        )

        user_prompt = str(user_prompt_raw)[:2000]

        try:
            requested_provider = normalize_provider(
                data.get(
                    "provider",
                    data.get("ai_provider", "meta"),
                )
            )
        except ValueError as exc:
            return error_response(
                error="INVALID_PROVIDER",
                status_code=400,
                message=str(exc),
                supported_providers=list(SUPPORTED_PROVIDERS),
            )

        if requested_provider not in SUPPORTED_PROVIDERS:
            audit_log(
                "ANALYZE_UNSUPPORTED_PROVIDER",
                {
                    "requested_provider": requested_provider,
                    "supported_providers": list(SUPPORTED_PROVIDERS),
                },
                success=False,
            )

            return error_response(
                error="UNSUPPORTED_PROVIDER",
                status_code=400,
                message=(
                    f"Provider '{requested_provider}' is not supported"
                ),
                requested_provider=requested_provider,
                supported_providers=list(SUPPORTED_PROVIDERS),
            )

        valid, normalized, errors = validate_landscape_input(data)

        if not valid:
            has_data_gate = any(
                "DATA_GATE #4231" in error
                for error in errors
            )

            audit_log(
                "ANALYZE_VALIDATION_FAIL",
                {
                    "input": data,
                    "errors": errors,
                    "requested_provider": requested_provider,
                },
                success=False,
            )

            status_code = 422 if has_data_gate else 400

            return jsonify({
                "success": False,
                "system": SYSTEM_NAME,
                "error": "VALIDATION_FAILED",
                "data_gate": (
                    "DATA_GATE #4231"
                    if has_data_gate
                    else "GENERAL_VALIDATION"
                ),
                "errors": errors,
            }), status_code

        # -------------------------------------------------------------------
        # Deterministic domain processing
        # -------------------------------------------------------------------

        boq_result = calculate_boq(
            area=normalized["area"],
            soil_type=normalized["soil_type"],
            slope_percent=normalized["slope_percent"],
            access_type=normalized["access_type"],
            spt=normalized.get("spt"),
            pile_count=normalized.get("pile_count", 24),
        )

        soil_result = classify_soil(
            normalized["soil_type"],
            normalized.get("spt"),
        )

        foundation_result = design_foundation(
            normalized["area"],
            normalized["soil_type"],
            normalized.get("spt"),
            normalized["slope_percent"],
        )

        plants_result = select_plants(
            normalized["soil_type"],
            normalized["area"],
        )

        material_result = get_material_palette(
            normalized["area"],
        )

        plant_count = plants_result.get("count", 0)

        leed_result = calculate_leed(
            normalized["area"],
            normalized["soil_type"],
            plant_count,
        )

        deterministic_result = {
            "boq": boq_result,
            "soil": soil_result,
            "foundation": foundation_result,
            "plants": plants_result,
            "material": material_result,
            "leed": leed_result,
            "input_normalized": normalized,
        }

        # -------------------------------------------------------------------
        # AI explanation only
        # -------------------------------------------------------------------

        ai_result, actual_provider = execute_ai_provider(
            requested_provider,
            deterministic_result,
            user_prompt,
        )

        response = {
            "success": True,
            "system": SYSTEM_NAME,
            "version": VERSION,
            "pipeline": (
                "USER INPUT -> VALIDATION -> "
                "DETERMINISTIC DOMAIN ENGINE (6) -> "
                "VERIFIED RESULT -> AI EXPLANATION ONLY -> "
                "RESPONSE -> AUDIT"
            ),
            "rule_6_compliance": (
                "Deterministic result built before AI call. "
                "AI explanation cannot replace BOQ numbers."
            ),
            "input_normalized": normalized,
            "deterministic_result": deterministic_result,
            "ai_explanation": ai_result,
            "ai_provider_requested": requested_provider,
            "ai_provider_used": actual_provider,
            "provider_evidence_consistent": (
                requested_provider == actual_provider
            ),
            "provider_config_status": {
                "meta": meta_config(),
                "gemini": gemini_config(),
                "modal": modal_config(),
            },
            "missing_api_key_behavior": (
                "Deterministic result remains available and "
                "the selected adapter returns a controlled fallback."
            ),
            "audit": "Logged to /tmp/champ_audit.log",
        }

        audit_log(
            "ANALYZE_SUCCESS",
            {
                "area": normalized["area"],
                "soil": normalized["soil_type"],
                "grand_total": boq_result["grand_total"],
                "provider_requested": requested_provider,
                "provider_used": actual_provider,
                "provider_evidence_consistent": (
                    requested_provider == actual_provider
                ),
                "ai_success": ai_result.get("success", False),
                "ai_source": ai_result.get("source"),
            },
            success=True,
        )

        return jsonify(response)

    except Exception as exc:
        audit_log(
            "ANALYZE_ENGINE_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
                "trace": traceback.format_exc()[:1000],
            },
            success=False,
        )

        return error_response(
            error="ENGINE_ERROR",
            status_code=500,
            message="Landscape analysis failed",
        )


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

@app.route("/api/audit/logs", methods=["GET"])
def audit_logs():
    try:
        raw_limit = request.args.get("limit", "50")

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            return error_response(
                error="INVALID_LIMIT",
                status_code=400,
                message="limit must be an integer",
            )

        limit = max(1, min(limit, 100))

        logs = get_audit_logs(limit)

        return jsonify({
            "success": True,
            "system": SYSTEM_NAME,
            "audit_log_path": "/tmp/champ_audit.log",
            "count": len(logs),
            "limit": limit,
            "logs": logs,
            "security_notice": (
                "Application-level authentication is not yet implemented "
                "for this endpoint."
            ),
        })

    except Exception as exc:
        audit_log(
            "AUDIT_LOG_READ_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            },
            success=False,
        )

        return error_response(
            error="AUDIT_LOG_READ_ERROR",
            status_code=500,
            message="Unable to read audit logs",
        )


# ---------------------------------------------------------------------------
# Soil classification
# ---------------------------------------------------------------------------

@app.route("/api/soil/classify", methods=["POST"])
def soil_classify():
    try:
        data = request.get_json(silent=True) or {}

        if not isinstance(data, dict):
            return error_response(
                error="INVALID_JSON_BODY",
                status_code=400,
                message="JSON body must be an object",
            )

        soil_type = data.get("soil_type", "Mollisols")
        spt = data.get("spt")

        result = classify_soil(
            soil_type,
            spt,
        )

        return jsonify({
            "success": True,
            "system": SYSTEM_NAME,
            "soil": result,
        })

    except Exception as exc:
        audit_log(
            "SOIL_CLASSIFY_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            },
            success=False,
        )

        return error_response(
            error="SOIL_CLASSIFY_ERROR",
            status_code=500,
            message="Soil classification failed",
        )


# ---------------------------------------------------------------------------
# Foundation design
# ---------------------------------------------------------------------------

@app.route("/api/foundation/design", methods=["POST"])
def foundation_design():
    try:
        data = request.get_json(silent=True) or {}

        if not isinstance(data, dict):
            return error_response(
                error="INVALID_JSON_BODY",
                status_code=400,
                message="JSON body must be an object",
            )

        area = data.get("area", 100)
        soil_type = data.get("soil_type", "Mollisols")
        spt = data.get("spt")
        slope_percent = data.get("slope_percent", 0)

        result = design_foundation(
            area,
            soil_type,
            spt,
            slope_percent,
        )

        return jsonify({
            "success": True,
            "system": SYSTEM_NAME,
            "foundation": result,
        })

    except Exception as exc:
        audit_log(
            "FOUNDATION_DESIGN_ERROR",
            {
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            },
            success=False,
        )

        return error_response(
            error="FOUNDATION_DESIGN_ERROR",
            status_code=500,
            message="Foundation design failed",
        )


# ---------------------------------------------------------------------------
# Local development entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting {SYSTEM_NAME} v{VERSION} on port {port}")
    print(f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")
    print(f"Meta configured: {meta_configured()}")
    print(f"Gemini configured: {gemini_configured()}")
    print(f"Modal configured: {modal_configured()}")
    print(
        "Evidence > Claims - Repair > Rebuild - "
        "One CHAMP > Many Versions"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
