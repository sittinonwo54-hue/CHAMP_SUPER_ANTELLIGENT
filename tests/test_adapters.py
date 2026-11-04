
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.meta_adapter import is_configured as meta_is_configured, get_config_status as meta_config_status, META_API_BASE_CANONICAL
from adapters.gemini_adapter import is_configured as gemini_is_configured, get_config_status as gemini_config_status

def test_meta_api_base_canonical():
    assert META_API_BASE_CANONICAL == "https://api.meta.ai/v1"
    status = meta_config_status()
    assert status['api_base_canonical'] == "https://api.meta.ai/v1"
    assert status['chat_endpoint'] == "https://api.meta.ai/v1/chat/completions"

def test_meta_not_configured_returns_false_without_key():
    # Ensure env not set for test
    old = os.getenv("MODEL_API_KEY")
    old2 = os.getenv("META_API_KEY")
    if "MODEL_API_KEY" in os.environ:
        del os.environ["MODEL_API_KEY"]
    if "META_API_KEY" in os.environ:
        del os.environ["META_API_KEY"]
    try:
        assert meta_is_configured() == False
        # generate_explanation should return API_KEY_NOT_CONFIGURED not crash
        from adapters.meta_adapter import generate_explanation
        result = generate_explanation({"boq":{"grand_total":100000}}, "test")
        assert result['success'] == False
        assert result['error'] == "API_KEY_NOT_CONFIGURED"
    finally:
        if old:
            os.environ["MODEL_API_KEY"] = old
        if old2:
            os.environ["META_API_KEY"] = old2

def test_gemini_not_configured_returns_false():
    old = os.getenv("GEMINI_API_KEY")
    old2 = os.getenv("GOOGLE_API_KEY")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]
    try:
        assert gemini_is_configured() == False
        from adapters.gemini_adapter import generate_explanation
        result = generate_explanation({"boq":{"grand_total":100000}}, "test")
        assert result['success'] == False
        assert result['error'] == "API_KEY_NOT_CONFIGURED"
    finally:
        if old:
            os.environ["GEMINI_API_KEY"] = old
        if old2:
            os.environ["GOOGLE_API_KEY"] = old2

def test_gemini_sdk_is_google_genai():
    status = gemini_config_status()
    assert status['sdk'] == "google-genai"
    assert "gemini-3.8-flash" in status['model'] or "gemini" in status['model']
