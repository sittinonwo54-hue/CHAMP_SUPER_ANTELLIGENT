import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module
from app import app


@pytest.fixture(autouse=True)
def prevent_external_provider_requests(monkeypatch):
    """Keep every app test offline unless its provider behavior is mocked."""

    def fake_explanation(provider):
        def explain(verified_result, prompt=None):
            return {
                "success": True,
                "explanation": f"{provider} test explanation",
                "verified_context_used": verified_result,
                "source": "TEST_MOCK",
            }

        return explain

    monkeypatch.setattr(app_module, "meta_explain", fake_explanation("meta"))
    monkeypatch.setattr(app_module, "gemini_explain", fake_explanation("gemini"))
    monkeypatch.setattr(app_module, "modal_explain", fake_explanation("modal"))


def _landscape_payload(**overrides):
    payload = {
        "area": 100,
        "soil_type": "Mollisols",
        "slope_percent": 2,
        "access_type": "normal",
        "spt": 20,
        "prompt": "Explain this garden",
    }
    payload.update(overrides)
    return payload


def test_health_endpoint():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["meta_api_base_canonical"] == "https://api.meta.ai/v1"
    assert data["gemini_sdk"] == "google-genai"
    assert "rule_6_compliance" in data
    assert data["status"] == "healthy"
    assert "modal" in data["supported_providers"]
    assert "modal_config" in data
    assert "modal_configured" in data


def test_root_endpoint():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["system"] == "CHAMP_SUPER_ANTELLIGENT"


def test_boq_calculate_endpoint():
    client = app.test_client()
    resp = client.post(
        "/api/boq/calculate",
        json={"area": 150, "soil_type": "Vertisols", "slope_percent": 5,
              "access_type": "narrow", "spt": 8},
    )
    # Should succeed with SPT for Vertisols
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "boq" in data


def test_boq_calculate_data_gate_4231_block():
    client = app.test_client()
    resp = client.post(
        "/api/boq/calculate",
        json={"area": 150, "soil_type": "Vertisols", "slope_percent": 5,
              "access_type": "narrow"},
    )
    # Should block without SPT
    assert resp.status_code in [400, 422]
    data = resp.get_json()
    assert data["success"] is False
    assert "DATA_GATE #4231" in str(data["errors"])


def test_analyze_landscape_full_pipeline():
    client = app.test_client()
    resp = client.post("/api/analyze-landscape", json=_landscape_payload())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "deterministic_result" in data
    assert "boq" in data["deterministic_result"]
    assert "ai_explanation" in data
    # Rule 6: deterministic result preserved
    assert data["deterministic_result"]["boq"]["grand_total"] > 0


def test_audit_logs_endpoint():
    client = app.test_client()
    resp = client.get("/api/audit/logs?limit=10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True


def test_modal_provider_routes_only_to_modal(monkeypatch):
    calls = {"meta": 0, "gemini": 0, "modal": 0}

    def record(provider):
        def explain(verified_result, prompt):
            calls[provider] += 1
            return {"success": True, "explanation": "mock", "verified_context_used": verified_result}

        return explain

    monkeypatch.setattr(app_module, "meta_explain", record("meta"))
    monkeypatch.setattr(app_module, "gemini_explain", record("gemini"))
    monkeypatch.setattr(app_module, "modal_explain", record("modal"))

    response = app.test_client().post(
        "/api/analyze-landscape", json=_landscape_payload(provider="modal")
    )
    data = response.get_json()
    assert response.status_code == 200
    assert calls == {"meta": 0, "gemini": 0, "modal": 1}
    assert data["ai_provider_requested"] == "modal"
    assert data["ai_provider_used"] == "modal"
    assert data["provider_evidence_consistent"] is True
    assert "deterministic_result" in data
    assert "boq" in data["deterministic_result"]
    assert data["deterministic_result"]["boq"]["grand_total"] > 0


def test_meta_provider_routing(monkeypatch):
    calls = []

    def mock_meta(verified_result, prompt):
        calls.append((verified_result, prompt))
        return {"success": True, "explanation": "mock Meta"}

    monkeypatch.setattr(app_module, "meta_explain", mock_meta)
    response = app.test_client().post(
        "/api/analyze-landscape", json=_landscape_payload(provider="meta")
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(calls) == 1
    assert data["ai_provider_requested"] == "meta"
    assert data["ai_provider_used"] == "meta"
    assert data["provider_evidence_consistent"] is True


def test_gemini_provider_routing(monkeypatch):
    calls = []

    def mock_gemini(verified_result, prompt):
        calls.append((verified_result, prompt))
        return {"success": True, "explanation": "mock Gemini"}

    monkeypatch.setattr(app_module, "gemini_explain", mock_gemini)
    response = app.test_client().post(
        "/api/analyze-landscape", json=_landscape_payload(provider="gemini")
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(calls) == 1
    assert data["ai_provider_requested"] == "gemini"
    assert data["ai_provider_used"] == "gemini"
    assert data["provider_evidence_consistent"] is True


def test_unknown_provider_is_rejected():
    response = app.test_client().post(
        "/api/analyze-landscape",
        json=_landscape_payload(provider="unknown-provider"),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"] == "UNSUPPORTED_PROVIDER"
    assert data["requested_provider"] == "unknown-provider"
    assert {"meta", "gemini", "modal"}.issubset(data["supported_providers"])


def test_default_provider_routes_to_meta(monkeypatch):
    calls = []

    def mock_meta(verified_result, prompt):
        calls.append((verified_result, prompt))
        return {"success": True, "explanation": "mock Meta"}

    monkeypatch.setattr(app_module, "meta_explain", mock_meta)
    response = app.test_client().post(
        "/api/analyze-landscape", json=_landscape_payload()
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(calls) == 1
    assert data["ai_provider_requested"] == "meta"
    assert data["ai_provider_used"] == "meta"
    assert data["provider_evidence_consistent"] is True


def test_modal_provider_failure_preserves_deterministic_result(monkeypatch):
    def fail_modal(verified_result, prompt):
        raise RuntimeError("controlled provider failure")

    monkeypatch.setattr(app_module, "modal_explain", fail_modal)
    response = app.test_client().post(
        "/api/analyze-landscape", json=_landscape_payload(provider="modal")
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "deterministic_result" in data
    assert "boq" in data["deterministic_result"]
    assert data["deterministic_result"]["boq"]["grand_total"] > 0
    assert data["ai_provider_requested"] == "modal"
    assert data["ai_provider_used"] == "modal"
    assert data["provider_evidence_consistent"] is True
    assert data["ai_explanation"]["success"] is False
    assert data["ai_explanation"]["error"] == "AI_PROVIDER_EXCEPTION"
    assert data["ai_explanation"]["detail"] == "controlled provider failure"
