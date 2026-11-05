import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.meta_adapter import (
    is_configured as meta_is_configured,
    get_config_status as meta_config_status,
    META_API_BASE_CANONICAL,
)
from adapters.gemini_adapter import (
    is_configured as gemini_is_configured,
    get_config_status as gemini_config_status,
)
from adapters import modal_adapter


def test_meta_api_base_canonical():
    assert META_API_BASE_CANONICAL == "https://api.meta.ai/v1"
    status = meta_config_status()
    assert status["api_base_canonical"] == "https://api.meta.ai/v1"
    assert status["chat_endpoint"] == "https://api.meta.ai/v1/chat/completions"


def test_meta_not_configured_returns_false_without_key(monkeypatch):
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("META_API_KEY", raising=False)
    assert meta_is_configured() is False
    # generate_explanation should return API_KEY_NOT_CONFIGURED not crash
    from adapters.meta_adapter import generate_explanation
    result = generate_explanation({"boq": {"grand_total": 100000}}, "test")
    assert result["success"] is False
    assert result["error"] == "API_KEY_NOT_CONFIGURED"


def test_gemini_not_configured_returns_false(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert gemini_is_configured() is False
    from adapters.gemini_adapter import generate_explanation
    result = generate_explanation({"boq": {"grand_total": 100000}}, "test")
    assert result["success"] is False
    assert result["error"] == "API_KEY_NOT_CONFIGURED"


def test_gemini_sdk_is_google_genai():
    status = gemini_config_status()
    assert status["sdk"] == "google-genai"
    assert "gemini-3.8-flash" in status["model"] or "gemini" in status["model"]


def test_modal_missing_token_uses_local_fallback(monkeypatch):
    monkeypatch.delenv("MODAL_PROXY_TOKEN", raising=False)
    deterministic_result = {"boq": {"grand_total": 12345.67}, "marker": "unchanged"}

    assert modal_adapter.is_configured() is False
    result = modal_adapter.generate_explanation(deterministic_result, "test")

    assert result["success"] is False
    assert result["error"] == "MODAL_NOT_CONFIGURED"
    assert result["source"] == "LOCAL_FALLBACK"
    assert result["verified_context_used"] == deterministic_result


def test_modal_synthetic_token_format_configuration(monkeypatch):
    # Synthetic format-only value; this test does not perform network requests.
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-synthetic-test-token.ws-test")
    status = modal_adapter.get_config_status()

    assert status["configured"] is True
    assert status["provider"] == "modal"
    assert modal_adapter.is_configured() is True
