import os, re, json
from flask import Flask, request, jsonify
from boq_engine import calculate_boq
from soil_engine import classify_soil
from plant_engine import select_plants
from astm_engine import spt_spec, expansion_index
from leed_engine import calculate_leed
from sop_engine import get_sop
from adapters.meta_adapter import info as meta_info
from adapters.gemini_adapter import info as gemini_info
from adapters.modal_adapter import info as modal_info
app = Flask(__name__)
def sanitize(v):
    if not isinstance(v, str):
        return v
    return v if re.match(r"^[a-zA-Z0-9 _\-.()%]+$", v) and len(v) <= 100 else "INVALID"
@app.route("/")
def home():
    return jsonify({"system": "CHAMP_SUPER_ANTELLIGENT", "status": "ok", "engines": 6, "adapters": ["meta", "gemini", "modal"]})
@app.route("/api/health")
def health():
    return jsonify({"system": "CHAMP_SUPER_ANTELLIGENT", "provider_registry": ["meta", "gemini", "modal"], "meta": meta_info(), "gemini": gemini_info(), "modal": modal_info(), "rule_6": "deterministic-before-AI", "data_gate": "#4231"})
@app.route("/api/boq/calculate", methods=["POST"])
def boq():
    d = request.get_json(force=True) or {}
    area = d.get("area"); soil = d.get("soil_type", "Mollisols"); spt = d.get("spt_n_value")
    if soil == "Vertisols" and spt is None:
        return jsonify({"error": "BLOCK - DATA_GATE #4231 - Vertisols requires SPT", "code": "#4231"}), 400
    if "Gm." in str(d) or "จุล" in str(d):
        return jsonify({"error": "BLOCK - Ethical Shield - Gm."}), 403
    result = calculate_boq(area, soil, d.get("slope_pct", 0), d.get("access", "normal"), spt)
    return jsonify(result)
@app.route("/api/analyze-landscape", methods=["POST"])
def analyze():
    d = request.get_json(force=True) or {}
    area = d.get("area", 100); clay = d.get("clay_pct"); cole = d.get("cole"); spt = d.get("spt_n_value")
    soil = classify_soil(clay, cole, spt)
    if soil.get("blocked"):
        return jsonify(soil), 400
    order = soil.get("order", "Mollisols")
    if order.startswith("Mollisols"):
        order = "Mollisols"
    boq = calculate_boq(area, order, d.get("slope_pct", 0), d.get("access", "normal"), spt)
    plants = select_plants(order)
    return jsonify({"system": "CHAMP_SUPER_ANTELLIGENT", "soil": soil, "boq": boq, "plants": plants, "astm_spt": spt_spec(), "leed": calculate_leed(d.get("leed_points", {})), "sop": get_sop(), "note": "Deterministic authoritative. AI explanation only. 135 Agents / Plant 500 / Projects 100 / Vector DB 384 = [DOCUMENTATION_ONLY]"})
@app.route("/api/audit/logs")
def audit():
    return jsonify({"audit": "simple file log /tmp/champ_audit.log - CODE READY", "rate_limiting": "NOT_IMPLEMENTED", "api_auth": "NOT_IMPLEMENTED"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
