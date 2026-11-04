from datetime import datetime, timezone
import os, json
AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "champ_audit.log")
if os.path.exists("/tmp") and os.access("/tmp", os.W_OK):
    AUDIT_LOG_PATH = "/tmp/champ_audit.log"
def audit_log(action, data, success=True):
    try:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with open(AUDIT_LOG_PATH,"a",encoding="utf-8") as f:
            f.write(json.dumps({"timestamp":ts,"action":action,"data":data,"success":success})+"\n")
    except: pass
def get_audit_logs(limit=50):
    try:
        if not os.path.exists(AUDIT_LOG_PATH): return []
        with open(AUDIT_LOG_PATH,"r",encoding="utf-8") as fo:
            lines=fo.readlines()[-limit:]
            return [json.loads(l) for l in lines if l.strip()]
    except: return []
