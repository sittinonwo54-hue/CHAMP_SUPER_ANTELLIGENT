
"""
app.py - CHAMP_SUPER_ANTELLIGENT - CANONICAL RUNTIME per APP_PY_FIXED.md
Pipeline:
USER INPUT
  ↓
VALIDATION (validation.py - DATA_GATE #4231)
  ↓
DETERMINISTIC DOMAIN ENGINE (6 engines)
  ↓
VERIFIED BOQ / SOIL / SITE RESULT
  ↓
AI PROVIDER (Meta OR Gemini) - EXPLANATION ONLY per Rule 6
  ↓
STRUCTURED RESPONSE
  ↓
AUDIT LOG (audit.py)

Endpoints:
GET / - root
GET /api/health - health check with meta_api_base_canonical = https://api.meta.ai/v1, gemini_sdk = google-genai, rule_6_compliance
POST /api/boq/calculate - BOQ deterministic
POST /api/analyze-landscape - full pipeline with deterministic first, AI explanation second
GET /api/audit/logs - audit logs

Security:
- No hardcoded secrets - env only
- Missing API key does NOT crash - returns API_KEY_NOT_CONFIGURED per APP_PY_FIXED.md
- sanitize_input regex ^[a-zA-Z0-9 _-.()%]+$ length 100
- DATA_GATE #4231 SPT mandatory for Vertisols
- Audit logging to /tmp/champ_audit.log
- CORS enabled
- Rule 6 compliance: deterministic summary built BEFORE AI call, LLM must NOT invent BOQ values

Dependencies: Flask==3.0.3, Flask-Cors==4.0.1, requests==2.32.3, python-dotenv==1.0.1, gunicorn==22.0.0, google-genai>=0.3.0

Actual runtime reality vs old doc:
OLD DOC claimed Node.js Express stack - DOCUMENTATION ONLY - NOT VERIFIED
REALITY: Flask garden AI - BOQ calculation, soil taxonomy, foundation SOP, Meta/Gemini explanation - CODE READY
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Werkzeug fallback shim for offline per APP_PY_FIXED.md
try:
    from werkzeug.serving import run_simple
except ImportError:
    run_simple = None

from utils.validation import validate_landscape_input, sanitize_input
from utils.audit import audit_log, get_audit_logs

# Engines - 6 deterministic engines - CODE READY per reality check
from engines.boq_engine import calculate_boq, BASE_RATE, BASE_RATE_EXACT
from engines.soil_engine import classify_soil, get_all_usda_orders, get_all_wrb_groups
from engines.foundation_engine import design_foundation
from engines.plant_engine import select_plants, get_all_plants
from engines.material_engine import get_material_palette
from engines.leed_engine import calculate_leed

# Adapters - 2 AI adapters - CODE READY
from adapters.meta_adapter import generate_explanation as meta_explain, get_config_status as meta_config, is_configured as meta_configured, META_API_BASE_CANONICAL
from adapters.gemini_adapter import generate_explanation as gemini_explain, get_config_status as gemini_config, is_configured as gemini_configured

app = Flask(__name__)
CORS(app)

# System identity per INDEX_CARD_REAL_DATA_ONLY.md
SYSTEM_NAME = "CHAMP_SUPER_ANTELLIGENT"
VERSION = "1.0.0-hackathon"
TAGLINE = "Architecture Meets Nature Enhanced by AI"

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "system": SYSTEM_NAME,
        "version": VERSION,
        "tagline": TAGLINE,
        "canonical_folder": "https://drive.google.com/drive/folders/1OCimGhRhg-QazMl_30u7Yk2axais-Vr7",
        "architecture": "USER INPUT → VALIDATION (DATA_GATE #4231) → DETERMINISTIC DOMAIN ENGINE (6 engines) → VERIFIED RESULT → AI EXPLANATION ONLY → RESPONSE → AUDIT",
        "deterministic_engines": ["BOQ_ENGINE BaseRate 741", "SOIL_TAXONOMY 12 USDA Orders", "FOUNDATION_SOP Pile D30", "PLANT_KNOWLEDGE limited", "MATERIAL_PALETTE Thai 2024-2025", "LEED_V5 110pts"],
        "ai_adapters": ["Meta https://api.meta.ai/v1/chat/completions muse-spark-1.3", "Gemini google-genai gemini-3.8-flash"],
        "endpoints": ["/", "/api/health", "/api/boq/calculate", "/api/analyze-landscape", "/api/audit/logs"],
        "evidence": "Evidence > Claims - Repair > Rebuild - One CHAMP > Many Versions",
        "rule_6_compliance": "LLM must NOT invent BOQ values - deterministic summary built BEFORE AI call",
        "real_projects": {"88_1": "432sqm 320207 THB BaseRate 741 = 320207/432=741.21 validated 0.03% deviation", "PJ0014": "150sqm Vertisols 55% Narrow Slope 5% SPT 8 311753 THB vs runtime 510277.73 NOT VERIFIED per Rule 7"},
        "reality_check": "135 Agents DOCUMENTATION ONLY - actual 6 engines + 2 adapters - Plant 500 CLAIM vs 10-15 actual PARTIAL - Real Projects 100 CLAIM vs 2 actual PARTIAL"
    })

@app.route("/api/health", methods=["GET"])
def health():
    meta_status = meta_config()
    gemini_status = gemini_config()
    return jsonify({
        "status": "healthy",
        "system": SYSTEM_NAME,
        "version": VERSION,
        "meta_api_base_canonical": META_API_BASE_CANONICAL,
        "meta_config": meta_status,
        "meta_configured": meta_configured(),
        "gemini_sdk": "google-genai",
        "gemini_config": gemini_status,
        "gemini_configured": gemini_configured(),
        "rule_6_compliance": "Deterministic before AI - CODE READY",
        "data_gate_4231": "SPT mandatory for Vertisols - CODE READY per validation.py",
        "deterministic_engines": {
            "boq_engine": "CODE READY - BaseRate 741 = 320207/432",
            "soil_taxonomy": "CODE READY - 12 USDA Orders",
            "foundation_sop": "CODE READY - Pile D30 L2-3m SPT>15, Beam 20x40, Barrier HDPE80cm, Drain PVC4in",
            "plant_knowledge": "PARTIAL - 10-15 species vs 500 claim",
            "material_palette": "PARTIAL - Thai 2024-2025 sample",
            "leed_v5": "PARTIAL - 110 points structure CODE READY"
        },
        "security": {
            "no_hardcoded_secrets": "CODE READY - env only",
            "sanitize_input": "CODE READY - regex ^[a-zA-Z0-9 _-.()%]+$ length 100",
            "audit_log": "CODE READY - /tmp/champ_audit.log",
            "hmac_gate_jul_pleng": "DOCUMENTATION ONLY - NOT VERIFIED - actual env-only",
            "rate_limit_100_15min": "DOCUMENTATION ONLY - NOT VERIFIED",
            "fernet": "DOCUMENTATION ONLY",
            "kill_switch": "DOCUMENTATION ONLY - NOT VERIFIED"
        },
        "reality": {
            "agents_135": "DOCUMENTATION ONLY - actual 0 orchestration",
            "subsystems_15_on_off": "DOCUMENTATION ONLY - no endpoint /api/org/subsystem/*/on/off",
            "plant_500": "DOCUMENTATION ONLY - actual 10-15",
            "projects_100": "DOCUMENTATION ONLY - actual 2",
            "boq_100_items": "PARTIAL - sample 5-10",
            "sop_45_days_gantt": "DOCUMENTATION ONLY",
            "vector_db_384_dim": "DOCUMENTATION ONLY"
        },
        "official_refs": {
            "meta_api": "https://api.meta.ai/v1 and https://dev.meta.ai/docs",
            "gemini_sdk": "https://googleapis.github.io/python-genai/",
            "usda": "https://www.nrcs.usda.gov",
            "fao_wrb": "https://www.fao.org/soils-portal",
            "astm_d1586": "https://www.astm.org/d1586-d1586m-18.html",
            "astm_d4829": "https://www.astm.org/d4829-21.html",
            "usgbc_leed_v5": "https://www.usgbc.org/leed/v5",
            "iso_42001": "ISO/IEC 42001:2023"
        }
    })

@app.route("/api/boq/calculate", methods=["POST"])
def boq_calculate():
    try:
        data = request.get_json() or {}
        valid, normalized, errors = validate_landscape_input(data)
        
        if not valid:
            # Check if DATA_GATE #4231
            has_data_gate = any("DATA_GATE #4231" in e for e in errors)
            audit_log("BOQ_CALCULATE_VALIDATION_FAIL", {"input": data, "errors": errors, "data_gate_4231": has_data_gate}, success=False)
            status_code = 400 if not has_data_gate else 422
            return jsonify({
                "success": False,
                "error": "VALIDATION_FAILED",
                "data_gate": "DATA_GATE #4231" if has_data_gate else "GENERAL_VALIDATION",
                "errors": errors,
                "normalized": normalized,
                "evidence": "No SPT No build - SPT 3 points Depth 6m ASTM D1586 mandatory for Vertisols per #4231"
            }), status_code
        
        # Deterministic calculation
        boq_result = calculate_boq(
            area=normalized['area'],
            soil_type=normalized['soil_type'],
            slope_percent=normalized['slope_percent'],
            access_type=normalized['access_type'],
            spt=normalized.get('spt'),
            pile_count=normalized.get('pile_count', 24)
        )
        
        audit_log("BOQ_CALCULATE_SUCCESS", {"area": normalized['area'], "soil": normalized['soil_type'], "grand_total": boq_result['grand_total']}, success=True)
        
        return jsonify({
            "success": True,
            "system": SYSTEM_NAME,
            "engine": "BOQ_ENGINE - BaseRate 741 = 320207/432 - CODE READY",
            "input_normalized": normalized,
            "boq": boq_result,
            "validation": {"valid": valid, "errors": errors},
            "reality_notes": {
                "base_rate_validation_88_1": "432*741=320112 vs invoice 320207 deviation 0.03% - CODE READY base alone",
                "double_count_risk": "With add-ons 681707 vs 320207 = 112% over - indicates BaseRate already includes components",
                "pj0014": "Reference 311753 vs runtime 510277.73 for same inputs - PJ0014_CALIBRATION = NOT VERIFIED per Rule 7 - keep truthful"
            }
        })
    except Exception as e:
        audit_log("BOQ_CALCULATE_ENGINE_ERROR", {"error": str(e), "input": request.get_json()}, success=False)
        return jsonify({"success": False, "error": "ENGINE_ERROR", "message": str(e)}), 500

@app.route("/api/analyze-landscape", methods=["POST"])
def analyze_landscape():
    """
    Full pipeline per APP_PY_FIXED.md:
    USER INPUT -> VALIDATION (DATA_GATE #4231) -> DETERMINISTIC DOMAIN ENGINE -> VERIFIED RESULT -> AI EXPLANATION ONLY -> STRUCTURED RESPONSE -> AUDIT
    Rule 6 compliance: deterministic summary built BEFORE AI call, LLM must NOT invent BOQ values
    """
    try:
        data = request.get_json() or {}
        user_prompt = data.get('prompt', data.get('query', 'Analyze landscape project'))
        
        valid, normalized, errors = validate_landscape_input(data)
        if not valid:
            has_data_gate = any("DATA_GATE #4231" in e for e in errors)
            audit_log("ANALYZE_VALIDATION_FAIL", {"input": data, "errors": errors}, success=False)
            return jsonify({"success": False, "error": "VALIDATION_FAILED", "data_gate": "DATA_GATE #4231" if has_data_gate else "GENERAL", "errors": errors}), 400 if not has_data_gate else 422
        
        # DETERMINISTIC DOMAIN ENGINES - 6 engines - CODE READY
        boq_result = calculate_boq(
            area=normalized['area'],
            soil_type=normalized['soil_type'],
            slope_percent=normalized['slope_percent'],
            access_type=normalized['access_type'],
            spt=normalized.get('spt'),
            pile_count=normalized.get('pile_count', 24)
        )
        
        soil_result = classify_soil(normalized['soil_type'], normalized.get('spt'))
        foundation_result = design_foundation(normalized['area'], normalized['soil_type'], normalized.get('spt'), normalized['slope_percent'])
        plants_result = select_plants(normalized['soil_type'], normalized['area'])
        material_result = get_material_palette(normalized['area'])
        leed_result = calculate_leed(normalized['area'], normalized['soil_type'], plants_result['count'])
        
        # VERIFIED DOMAIN RESULT - deterministic
        deterministic_result = {
            "boq": boq_result,
            "soil": soil_result,
            "foundation": foundation_result,
            "plants": plants_result,
            "material": material_result,
            "leed": leed_result,
            "input_normalized": normalized
        }
        
        # AI EXPLANATION LAYER - EXPLANATION ONLY per Rule 6 - must NOT invent BOQ values
        # Deterministic summary built BEFORE AI call per CANONICAL_GATE.md
        provider = data.get('provider', data.get('ai_provider', 'meta')).lower()
        if provider == 'gemini':
            ai_result = gemini_explain(deterministic_result, user_prompt)
        else:
            ai_result = meta_explain(deterministic_result, user_prompt)
        
        # STRUCTURED RESPONSE
        response = {
            "success": True,
            "system": SYSTEM_NAME,
            "version": VERSION,
            "pipeline": "USER INPUT -> VALIDATION -> DETERMINISTIC DOMAIN ENGINE (6) -> VERIFIED RESULT -> AI EXPLANATION ONLY -> RESPONSE -> AUDIT",
            "rule_6_compliance": "Deterministic summary built BEFORE AI call - AI returns explanation only, BOQ numbers from calculate_boq() only - CODE READY",
            "input_normalized": normalized,
            "deterministic_result": deterministic_result,
            "ai_explanation": ai_result,
            "ai_provider_used": provider,
            "meta_config_status": meta_config(),
            "gemini_config_status": gemini_config(),
            "missing_api_key_behavior": "Returns API_KEY_NOT_CONFIGURED no crash per APP_PY_FIXED.md - CODE READY",
            "audit": "Logged to /tmp/champ_audit.log"
        }
        
        audit_log("ANALYZE_SUCCESS", {"area": normalized['area'], "soil": normalized['soil_type'], "grand_total": boq_result['grand_total'], "provider": provider, "ai_success": ai_result.get('success', False)}, success=True)
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        audit_log("ANALYZE_ENGINE_ERROR", {"error": str(e), "trace": traceback.format_exc()[:500]}, success=False)
        return jsonify({"success": False, "error": "ENGINE_ERROR", "message": str(e)}), 500

@app.route("/api/audit/logs", methods=["GET"])
def audit_logs():
    try:
        limit = int(request.args.get('limit', 50))
        logs = get_audit_logs(limit)
        return jsonify({"success": True, "system": SYSTEM_NAME, "audit_log_path": "/tmp/champ_audit.log", "count": len(logs), "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Additional endpoint for plant/material/leed direct access - convenience not required but useful for hackathon
@app.route("/api/soil/classify", methods=["POST"])
def soil_classify():
    try:
        data = request.get_json() or {}
        soil_type = data.get('soil_type', 'Mollisols')
        spt = data.get('spt')
        result = classify_soil(soil_type, spt)
        return jsonify({"success": True, "soil": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/foundation/design", methods=["POST"])
def foundation_design():
    try:
        data = request.get_json() or {}
        result = design_foundation(data.get('area',100), data.get('soil_type','Mollisols'), data.get('spt'), data.get('slope_percent',0))
        return jsonify({"success": True, "foundation": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # No hardcoded secrets - env only per security CODE READY
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"Starting {SYSTEM_NAME} v{VERSION} on port {port}")
    print(f"Meta API base canonical: {META_API_BASE_CANONICAL} - model: {os.getenv('META_MODEL','muse-spark-1.3')}")
    print(f"Gemini SDK: google-genai - model: {os.getenv('GEMINI_MODEL','gemini-3.8-flash')}")
    print(f"Evidence > Claims - Repair > Rebuild - One CHAMP > Many Versions")
    app.run(host="0.0.0.0", port=port, debug=debug)
