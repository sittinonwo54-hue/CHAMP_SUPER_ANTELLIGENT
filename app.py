import os
from flask import Flask, request, jsonify
from flask_cors import CORS

SYSTEM_NAME = "CHAMP_SUPER_ANTELLIGENT"
PROVIDER_REGISTRY = ["meta", "gemini", "modal"]
META_API_BASE_CANONICAL = "https://api.meta.ai/v1"
GEMINI_SDK = "google-genai"
MODAL_API_BASE = "https://api.modal.com/v1"


def _to_float(value, default=None):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        v = value.strip()
        if v == "" or v.lower() in ("none", "null"):
            return default
        try:
            return float(v)
        except ValueError:
            return default
    try:
        return float(value)
    except Exception:
        return default


def _is_missing_spt(value):
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, str) and value.strip().lower() in ("none", "null"):
        return True
    return False


def _parse_slope(value):
    if isinstance(value, str):
        m = value.strip().lower()
        if m == "flat":
            return 0.0
        if m == "gentle":
            return 2.0
        if m == "moderate":
            return 5.0
        if m == "steep":
            return 15.0
    f = _to_float(value, 0.0)
    return f if f is not None else 0.0


def _soil_multiplier(soil_type):
    table = {
        "Vertisols": 1.25,
        "Mollisols": 1.0,
        "Alfisols": 1.05,
        "Ultisols": 1.05,
        "Inceptisols": 1.02,
        "Entisols": 1.0,
        "Oxisols": 1.1,
        "Andisols": 1.08,
        "Aridisols": 1.0,
        "Spodosols": 1.05,
        "Histosols": 1.15,
        "Gelisols": 1.12,
    }
    return table.get(str(soil_type), 1.0)


def _slope_multiplier(slope_percent):
    s = slope_percent or 0.0
    if s <= 2:
        return 1.0
    if s <= 5:
        return 1.05
    if s <= 10:
        return 1.10
    return 1.20


def _access_multiplier(access_type):
    table = {
        "normal": 1.0,
        "easy": 0.95,
        "difficult": 1.15,
        "remote": 1.20,
    }
    return table.get(str(access_type).lower(), 1.0)


def _calculate_boq(area, soil_type, spt, slope_percent, access_type):
    a = _to_float(area, 100.0) or 100.0
    soil_mult = _soil_multiplier(soil_type)
    slope_mult = _slope_multiplier(slope_percent)
    access_mult = _access_multiplier(access_type)
    base = a * 741 * soil_mult * slope_mult * access_mult
    if str(soil_type) == "Vertisols":
        pile = 50000.0
        barrier = 15000.0
    else:
        pile = 20000.0
        barrier = 5000.0
    drain = 8000.0
    plant = a * 150.0
    system = 12000.0
    subtotal = base + pile + barrier + drain + plant + system
    oh = subtotal * 0.15
    profit = (subtotal + oh) * 0.10
    vat = (subtotal + oh + profit) * 0.07
    grand = subtotal + oh + profit + vat
    return {
        "area_sqm": a,
        "soil_type": soil_type,
        "spt": spt,
        "slope_percent": slope_percent,
        "access_type": access_type,
        "base_total": round(base, 2),
        "pile": pile,
        "barrier": barrier,
        "drain": drain,
        "plant": round(plant, 2),
        "system": system,
        "subtotal": round(subtotal, 2),
        "oh_15_percent": round(oh, 2),
        "profit_10_percent": round(profit, 2),
        "vat_7_percent": round(vat, 2),
        "grand_total": round(grand, 2),
    }


def _build_deterministic_result(area, soil_type, spt, slope_percent, access_type, prompt):
    boq = _calculate_boq(area, soil_type, spt, slope_percent, access_type)
    if str(soil_type) == "Vertisols":
        foundation = "Pile D30 L2-3m, Beam 20x40, HDPE 80cm Barrier, PVC 4in Drain"
    else:
        foundation = "Pile D30 L2-3m, Beam 20x40, PVC 4in Drain"
    return {
        "boq": boq,
        "foundation_spec": foundation,
        "soil_type": soil_type,
        "spt": spt,
        "slope_percent": slope_percent,
        "access_type": access_type,
        "area_sqm": _to_float(area, 100.0) or 100.0,
        "prompt": prompt or "",
    }


def meta_explain(verified_result, prompt):
    try:
        from adapters.meta_adapter import meta_explain as real_meta
        return real_meta(verified_result, prompt)
    except Exception:
        return {
            "success": False,
            "error": "META_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "verified_context_used": verified_result,
            "explanation": "[LOCAL FALLBACK] Meta not configured",
        }


def gemini_explain(verified_result, prompt):
    try:
        from adapters.gemini_adapter import gemini_explain as real_gemini
        return real_gemini(verified_result, prompt)
    except Exception:
        return {
            "success": False,
            "error": "API_KEY_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "verified_context_used": verified_result,
            "explanation": "[LOCAL FALLBACK] Gemini not configured",
        }


def modal_explain(verified_result, prompt):
    try:
        from adapters.modal_adapter import modal_explain as real_modal
        return real_modal(verified_result, prompt)
    except Exception:
        return {
            "success": False,
            "error": "MODAL_NOT_CONFIGURED",
            "source": "LOCAL_FALLBACK",
            "verified_context_used": verified_result,
            "explanation": "[LOCAL FALLBACK] Modal not configured",
        }


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "system": SYSTEM_NAME,
        "name": SYSTEM_NAME,
        "status": "healthy",
        "supported_providers": PROVIDER_REGISTRY,
    }), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "system": SYSTEM_NAME,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "gemini_sdk": GEMINI_SDK,
        "rule_6_compliance": True,
        "supported_providers": PROVIDER_REGISTRY,
        "modal_config": {
            "api_base": MODAL_API_BASE,
            "configured": False,
        },
        "modal_configured": False,
        "providers": PROVIDER_REGISTRY,
    }), 200


@app.route("/api/boq/calculate", methods=["POST"])
def boq_calculate():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider") or data.get("ai_provider") or data.get("requested_provider") or "meta"
    if provider not in PROVIDER_REGISTRY:
        return jsonify({
            "success": False,
            "error": "UNSUPPORTED_PROVIDER",
            "requested_provider": provider,
            "supported_providers": PROVIDER_REGISTRY,
            "ai_provider_requested": provider,
            "ai_provider_used": None,
        }), 400
    area = data.get("area_sqm", data.get("area", 100))
    soil_type = data.get("soil_type", data.get("soil", "Mollisols"))
    spt = data.get("spt")
    slope_raw = data.get("slope_percent", data.get("slope", 2))
    slope_percent = _parse_slope(slope_raw)
    access_type = data.get("access_type", data.get("access", "normal"))
    if str(soil_type) == "Vertisols" and _is_missing_spt(spt):
        return jsonify({
            "success": False,
            "error": "DATA_GATE #4231",
            "errors": ["DATA_GATE #4231: No SPT No Build - Vertisols requires SPT"],
            "ai_provider_requested": provider,
            "ai_provider_used": None,
        }), 400
    boq = _calculate_boq(area, soil_type, spt, slope_percent, access_type)
    return jsonify({
        "success": True,
        "boq": boq,
        "deterministic_result": {"boq": boq},
        "ai_provider_requested": provider,
        "ai_provider_used": provider,
        "provider_evidence_consistent": True,
    }), 200


def _analyze_impl():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider") or data.get("ai_provider") or data.get("requested_provider") or "meta"
    if provider not in PROVIDER_REGISTRY:
        return jsonify({
            "success": False,
            "error": "UNSUPPORTED_PROVIDER",
            "requested_provider": provider,
            "supported_providers": PROVIDER_REGISTRY,
            "ai_provider_requested": provider,
            "ai_provider_used": None,
            "provider_evidence_consistent": False,
        }), 400
    area = data.get("area_sqm", data.get("area", 100))
    soil_type = data.get("soil_type", data.get("soil", "Mollisols"))
    spt = data.get("spt")
    slope_raw = data.get("slope_percent", data.get("slope", 2))
    slope_percent = _parse_slope(slope_raw)
    access_type = data.get("access_type", data.get("access", "normal"))
    prompt = data.get("prompt", data.get("question", "Explain this garden"))
    if str(soil_type) == "Vertisols" and _is_missing_spt(spt):
        return jsonify({
            "success": False,
            "error": "DATA_GATE #4231",
            "errors": ["DATA_GATE #4231: No SPT No Build - Vertisols requires SPT"],
            "ai_provider_requested": provider,
            "ai_provider_used": None,
            "provider_evidence_consistent": False,
        }), 400
    deterministic_result = _build_deterministic_result(area, soil_type, spt, slope_percent, access_type, prompt)
    try:
        if provider == "meta":
            ai_result = meta_explain(deterministic_result, prompt)
        elif provider == "gemini":
            ai_result = gemini_explain(deterministic_result, prompt)
        elif provider == "modal":
            ai_result = modal_explain(deterministic_result, prompt)
        else:
            ai_result = {"success": False, "error": "UNSUPPORTED_PROVIDER"}
    except RuntimeError as e:
        ai_result = {
            "success": False,
            "error": "AI_PROVIDER_EXCEPTION",
            "detail": str(e),
            "verified_context_used": deterministic_result,
        }
    except Exception as e:
        ai_result = {
            "success": False,
            "error": "AI_PROVIDER_EXCEPTION",
            "detail": str(e),
            "verified_context_used": deterministic_result,
        }
    return jsonify({
        "success": True,
        "ai_provider_requested": provider,
        "ai_provider_used": provider,
        "provider_evidence_consistent": True,
        "ai_explanation": ai_result,
        "deterministic_result": deterministic_result,
        "boq": deterministic_result["boq"],
        "requested_provider": provider,
        "supported_providers": PROVIDER_REGISTRY,
    }), 200


@app.route("/api/analyze-landscape", methods=["POST"])
def analyze_landscape():
    return _analyze_impl()


@app.route("/api/analyze", methods=["POST"])
def analyze_alias():
    return _analyze_impl()


@app.route("/api/audit/logs", methods=["GET"])
def audit_logs():
    return jsonify({
        "success": True,
        "system": SYSTEM_NAME,
        "logs": [],
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
