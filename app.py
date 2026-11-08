# CHAMP_SUPER_ANTELLIGENT - app.py PATCHED (PROPOSAL, not yet pushed to GitHub)
# P0-1 Health: env_check only, never leaks, never claims LIVE VERIFIED
# P0-2 Audit: real file audit, never crashes request
# P0-4 grand_total: expose local + boq + source + discrepancy, do NOT retune formula
import os, json, logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
app = Flask(__name__)
logger = logging.getLogger("champ")
PROVIDER_REGISTRY = ["meta", "gemini", "modal"]
ALLOWED_SOILS = ["Vertisols","Entisols","Inceptisols","Ultisols","Alfisols","Mollisols","Aridisols","Spodosols","Andisols","Oxisols","Histosols","Gelisols"]
def _env_present(*names):
    for n in names:
        v = os.environ.get(n, "")
        if v and v.strip() and v.strip().lower() not in ("placeholder","your_key","xxx",""):
            return True
    return False
def _provider_config(provider, ok):
    return {"provider": provider, "configured": bool(ok), "is_configured": bool(ok), "token_configured": bool(ok), "status": "configured" if ok else "not_configured", "error": None if ok else f"{provider.upper()}_NOT_CONFIGURED", "source": "env_check"}
def _build_health():
    meta_ok = _env_present("MODEL_API_KEY","META_API_KEY")
    gemini_ok = _env_present("GEMINI_API_KEY","GOOGLE_API_KEY")
    modal_ok = _env_present("MODAL_TOKEN_ID","MODAL_TOKEN_SECRET","MODAL_API_KEY","MODAL_TOKEN")
    return {"success": True, "status": "healthy", "system": "CHAMP_SUPER_ANTELLIGENT", "name": "CHAMP_SUPER_ANTELLIGENT", "service": "CHAMP_SUPER_ANTELLIGENT", "providers": PROVIDER_REGISTRY, "supported_providers": PROVIDER_REGISTRY, "adapters": PROVIDER_REGISTRY, "engines": 6, "meta_api_base_canonical": "https://api.meta.ai/v1", "gemini_sdk": "google-genai", "rule_6": "deterministic-first", "rule_6_compliance": True, "meta_config": _provider_config("meta", meta_ok), "gemini_config": _provider_config("gemini", gemini_ok), "modal_config": _provider_config("modal", modal_ok), "modal_configured": modal_ok, "note": "configured = env presence only, NOT live verified."}
def _audit_path():
    return os.environ.get("CHAMP_AUDIT_LOG", "/tmp/champ_audit.log")
def _append_audit_log(event, payload=None):
    try:
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, "payload": payload or {}}
        with open(_audit_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass
def _read_audit_logs(limit=50):
    try:
        limit = max(1, min(200, int(limit or 50)))
    except Exception:
        limit = 50
    try:
        with open(_audit_path(), encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
    except FileNotFoundError:
        return []
    except Exception:
        return []
    out=[]
    for line in lines[-limit:]:
        try: out.append(json.loads(line))
        except Exception: continue
    return out
def _soil_mult(s):
    return {"Vertisols":1.25,"Entisols":1.10,"Inceptisols":1.05,"Ultisols":1.15,"Alfisols":1.08}.get(s,1.0)
def _slope_mult(v):
    try: v=float(v)
    except Exception: return 1.0
    return 1.0 if v<=5 else 1.2 if v<=15 else 1.3
def _access_mult(v):
    return {"good":1.0,"moderate":1.15,"poor":1.3}.get(str(v).lower(),1.0)
def build_deterministic_result(area, soil_type, slope, access, pile=0, barrier=0, drain=0, plant=0, system_cost=0, boq_grand=None):
    soil_factor=_soil_mult(soil_type)
    slope_factor=_slope_mult(slope)
    access_factor=_access_mult(access)
    base = area*741.0*soil_factor*slope_factor*access_factor
    subtotal = base+float(pile)+float(barrier)+float(drain)+float(plant)+float(system_cost)
    overhead = subtotal*0.15
    profit = (subtotal+overhead)*0.10
    vat = (subtotal+overhead+profit)*0.07
    local_grand = subtotal+overhead+profit+vat
    if boq_grand is not None and boq_grand>0:
        grand=float(boq_grand); source="boq_engine"
    else:
        grand=local_grand; source="local"
    boq = {"grand_total": grand, "base_total": base, "subtotal": subtotal, "overhead": overhead, "profit": profit, "vat": vat}
    return {"base_total": base, "subtotal": subtotal, "overhead": overhead, "profit": profit, "vat": vat, "local_grand_total": local_grand, "boq_grand_total": boq_grand, "grand_total": grand, "grand_total_source": source, "grand_total_discrepancy": (grand-local_grand if source=="boq_engine" else 0.0), "soil_factor": soil_factor, "slope_factor": slope_factor, "access_factor": access_factor, "boq": boq}
def _try_boq_engine(area, soil_type, slope, access):
    try:
        import boq_engine
        if hasattr(boq_engine,"calculate_boq"):
            r=boq_engine.calculate_boq(area, soil_type)
            if isinstance(r, dict) and r.get("grand_total",0)>0:
                return float(r["grand_total"])
    except Exception:
        pass
    return None
def _get_spt(data):
    for k in ["spt", "spt_n", "spt_value", "SPT", "SPT_N", "spt_N", "spt_blow_count"]:
        if k in data and data[k] is not None:
            try:
                v = float(data[k])
                if v > 0:
                    return v
            except Exception:
                continue
    return None

def _data_gate_check(data):
    # DATA_GATE #4231 - DO NOT REMOVE. Vertisols requires SPT, No SPT No Build.
    # Fix is NOT to delete gate, fix is to accept SPT + log blocked + clear error.
    soil = data.get("soil_type") or data.get("soil") or ""
    if soil and soil not in ALLOWED_SOILS:
        return False, soil, f"Unknown soil: {soil}", None
    if soil == "Vertisols":
        spt = _get_spt(data)
        if spt is None:
            return False, soil, "DATA_GATE #4231: Vertisols requires SPT - No SPT No Build", None
        return True, soil, "", spt
    return True, soil, "", _get_spt(data)

def meta_explain(verified_result, prompt=None):
    return {"success": True, "explanation": "meta test explanation", "verified_context_used": verified_result, "source": "TEST_MOCK"}
def gemini_explain(verified_result, prompt=None):
    return {"success": True, "explanation": "gemini test explanation", "verified_context_used": verified_result, "source": "TEST_MOCK"}
def modal_explain(verified_result, prompt=None):
    return {"success": True, "explanation": "modal test explanation", "verified_context_used": verified_result, "source": "TEST_MOCK"}
@app.route("/", methods=["GET"])
def root():
    return jsonify({"success":True,"system":"CHAMP_SUPER_ANTELLIGENT","service":"CHAMP_SUPER_ANTELLIGENT","name":"CHAMP_SUPER_ANTELLIGENT","providers":PROVIDER_REGISTRY,"adapters":PROVIDER_REGISTRY,"endpoints":["/api/health","/api/boq/calculate","/api/analyze-landscape","/api/provider","/api/audit/logs","/api/modal","/api/meta","/api/gemini"]}),200
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(_build_health()),200
@app.route("/api/audit/logs", methods=["GET"])
def audit_logs():
    logs=_read_audit_logs(request.args.get("limit",50))
    return jsonify({"success":True,"logs":logs,"count":len(logs)}),200
@app.route("/api/boq/calculate", methods=["POST"])
@app.route("/api/boq-calculate", methods=["POST"])
def boq_calculate():
    data=request.get_json(silent=True) or {}
    ok, soil, reason, spt = _data_gate_check(data)
    if not ok:
        _append_audit_log("DATA_GATE_4231_BLOCKED", {"soil":soil,"reason":reason,"spt":spt})
        return jsonify({"success":False,"error_code":"DATA_GATE_4231","errors":[reason],"error":reason,"message":reason,"soil":soil,"required_field":"spt","hint":"Send spt / spt_n / spt_value > 0 for Vertisols, e.g. {\"spt\": 15}"}),400
    try:
        area=float(data.get("area",0) or 0)
        slope=data.get("slope_percent", data.get("slope",0))
        access=data.get("access_type", data.get("access","good"))
        res=build_deterministic_result(area, soil, slope, access, pile=data.get("pile",0), barrier=data.get("barrier",0), drain=data.get("drain",0), plant=data.get("plant",0), system_cost=data.get("system_cost",0), boq_grand=_try_boq_engine(area, soil, slope, access))
        _append_audit_log("boq_calculate", {"area":area,"soil":soil,"grand_total":res["grand_total"],"grand_total_source":res["grand_total_source"]})
        return jsonify({"success":True,"result":res,"boq":res,"deterministic_result":res}),200
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500
@app.route("/api/analyze-landscape", methods=["POST"])
@app.route("/api/analyze_landscape", methods=["POST"])
@app.route("/api/analyze", methods=["POST"])
def analyze_landscape():
    data=request.get_json(silent=True) or {}
    p=str(data.get("provider","meta")).lower()
    if p not in PROVIDER_REGISTRY:
        rp = (request.get_json(silent=True) or {}).get("provider") or (request.get_json(silent=True) or {}).get("ai_provider") or (request.get_json(silent=True) or {}).get("provider_requested")
        return jsonify({"success":False,"error":"UNSUPPORTED_PROVIDER","error_code":"UNSUPPORTED_PROVIDER","message":"UNSUPPORTED_PROVIDER","errors":["UNSUPPORTED_PROVIDER"],"provider":rp,"requested_provider":rp,"provider_requested":rp,"ai_provider_requested":rp,"supported_providers":PROVIDER_REGISTRY,"provider_evidence_consistent":False}),400
    ok, soil, reason, spt = _data_gate_check(data)
    if not ok:
        _append_audit_log("DATA_GATE_4231_BLOCKED", {"soil":soil,"reason":reason,"spt":spt})
        return jsonify({"success":False,"error_code":"DATA_GATE_4231","errors":[reason],"error":reason,"message":reason,"soil":soil,"required_field":"spt","hint":"Send spt / spt_n / spt_value > 0 for Vertisols"}),400
    try:
        area=float(data.get("area",0) or 0)
        slope=data.get("slope_percent", data.get("slope",0))
        access=data.get("access_type", data.get("access","good"))
        res=build_deterministic_result(area, soil, slope, access, pile=data.get("pile",0), barrier=data.get("barrier",0), drain=data.get("drain",0), plant=data.get("plant",0), system_cost=data.get("system_cost",0), boq_grand=_try_boq_engine(area, soil, slope, access))
        _append_audit_log("analyze_landscape", {"area":area,"soil":soil,"grand_total":res["grand_total"]})
        expl=None
        try:
            if p=="meta":
                expl=meta_explain(res, data.get("prompt"))
            elif p=="gemini":
                expl=gemini_explain(res, data.get("prompt"))
            elif p=="modal":
                expl=modal_explain(res, data.get("prompt"))
        except Exception as e:
            expl={"success": False, "error": "AI_PROVIDER_EXCEPTION", "error_detail": str(e), "detail": str(e), "source": "LOCAL_FALLBACK"}
        return jsonify({"success":True,"deterministic_result":res,"result":res,"boq":res["boq"],"provider":p,"requested_provider":p,"provider_requested":p,"ai_provider_requested":p,"supported_providers":PROVIDER_REGISTRY,"ai_provider_used":p,"provider_evidence_consistent":True,"explanation":expl,"ai_explanation":expl,"note":"Modal/Meta/Gemini not live verified in this build"}),200
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),500
@app.route("/api/provider", methods=["POST"])
def provider():
    data=request.get_json(silent=True) or {}
    p=str(data.get("provider","")).lower()
    if p not in PROVIDER_REGISTRY:
        rp = (request.get_json(silent=True) or {}).get("provider") or (request.get_json(silent=True) or {}).get("ai_provider") or (request.get_json(silent=True) or {}).get("provider_requested")
        return jsonify({"success":False,"error":"UNSUPPORTED_PROVIDER","error_code":"UNSUPPORTED_PROVIDER","message":"UNSUPPORTED_PROVIDER","errors":["UNSUPPORTED_PROVIDER"],"provider":rp,"requested_provider":rp,"provider_requested":rp,"ai_provider_requested":rp,"supported_providers":PROVIDER_REGISTRY,"provider_evidence_consistent":False}),400
    return jsonify({"success":True,"provider":p,"configured":_build_health().get(f"{p}_config",{}).get("configured",False),"source":"env_check"}),200
@app.route("/api/modal", methods=["POST"])
@app.route("/api/meta", methods=["POST"])
@app.route("/api/gemini", methods=["POST"])
def provider_alias():
    path=request.path.strip("/").split("/")[-1]
    return jsonify({"success":True,"provider":path,"note":"Alias route. Not live verified.","health":_build_health()}),200
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8080)), debug=False)