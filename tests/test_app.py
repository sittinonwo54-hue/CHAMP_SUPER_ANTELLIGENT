
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_health_endpoint():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['meta_api_base_canonical'] == "https://api.meta.ai/v1"
    assert data['gemini_sdk'] == "google-genai"
    assert "rule_6_compliance" in data

def test_root_endpoint():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['system'] == "CHAMP_SUPER_ANTELLIGENT"

def test_boq_calculate_endpoint():
    client = app.test_client()
    resp = client.post("/api/boq/calculate", json={"area":150, "soil_type":"Vertisols", "slope_percent":5, "access_type":"narrow", "spt":8})
    # Should succeed with SPT for Vertisols
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] == True
    assert 'boq' in data

def test_boq_calculate_data_gate_4231_block():
    client = app.test_client()
    resp = client.post("/api/boq/calculate", json={"area":150, "soil_type":"Vertisols", "slope_percent":5, "access_type":"narrow"})
    # Should block without SPT
    assert resp.status_code in [400,422]
    data = resp.get_json()
    assert data['success'] == False
    assert "DATA_GATE #4231" in str(data['errors'])

def test_analyze_landscape_full_pipeline():
    client = app.test_client()
    resp = client.post("/api/analyze-landscape", json={"area":100, "soil_type":"Mollisols", "slope_percent":2, "access_type":"normal", "spt":20, "prompt":"Explain this garden"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] == True
    assert 'deterministic_result' in data
    assert 'boq' in data['deterministic_result']
    assert 'ai_explanation' in data
    # Rule 6: deterministic result preserved
    assert data['deterministic_result']['boq']['grand_total'] > 0

def test_audit_logs_endpoint():
    client = app.test_client()
    resp = client.get("/api/audit/logs?limit=10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] == True
