
"""
tests/test_validation.py - TC08 DATA_GATE #4231 - CODE READY per TEVV_PLAN
Per Rule 8: report exact tests collected/passed/failed/exit code - NOT claim PASSED without execution
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import sanitize_input, validate_area, validate_spt, validate_landscape_input

def test_sanitize_input_valid():
    assert sanitize_input("Vertisols") == "Vertisols"
    assert sanitize_input("normal") == "normal"
    assert sanitize_input("88_1") == "88_1"

def test_sanitize_input_invalid_chars():
    try:
        sanitize_input("DROP TABLE;")
        assert False, "Should raise ValueError for ;"
    except ValueError:
        assert True

def test_sanitize_input_length():
    try:
        sanitize_input("a"*101)
        assert False, "Should raise for >100"
    except ValueError:
        assert True

def test_validate_area_zero_returns_zero():
    assert validate_area(0) == 0.0
    assert validate_area(-5) == 0.0

def test_validate_area_over_10000_raises():
    try:
        validate_area(15000)
        assert False
    except ValueError:
        assert True

def test_validate_area_non_numeric_raises():
    try:
        validate_area("abc")
        assert False
    except ValueError:
        assert True

def test_validate_spt_none_raises_data_gate():
    try:
        validate_spt(None)
        assert False
    except ValueError as e:
        assert "DATA_GATE #4231" in str(e)

def test_validate_spt_range():
    assert validate_spt(8) == 8
    try:
        validate_spt(60)
        assert False
    except ValueError:
        assert True

def test_data_gate_4231_vertisols_no_spt_blocked():
    valid, normalized, errors = validate_landscape_input({"area":150, "soil_type":"Vertisols", "slope_percent":5, "access_type":"narrow"})
    assert valid == False
    assert any("DATA_GATE #4231" in e for e in errors)

def test_data_gate_4231_vertisols_with_spt_pass():
    valid, normalized, errors = validate_landscape_input({"area":150, "soil_type":"Vertisols", "slope_percent":5, "access_type":"narrow", "spt":8})
    assert valid == True
    assert len(errors)==0

def test_validate_landscape_non_vertisols_no_spt_allowed():
    valid, normalized, errors = validate_landscape_input({"area":100, "soil_type":"Mollisols", "slope_percent":2, "access_type":"normal"})
    assert valid == True

def test_area_zero_invalid():
    valid, normalized, errors = validate_landscape_input({"area":0, "soil_type":"Mollisols"})
    assert valid == False
