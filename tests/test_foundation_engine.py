
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engines.foundation_engine import design_foundation

def test_foundation_pile_required_vertisols_low_spt():
    result = design_foundation(150, "Vertisols", 8, 5)
    assert result['pile']['required'] == True
    assert result['pile']['diameter_cm'] == 30
    assert result['pile']['count'] == 24

def test_foundation_pile_not_required_high_spt():
    result = design_foundation(100, "Mollisols", 20, 0)
    assert result['pile']['required'] == False

def test_foundation_sop_specs():
    result = design_foundation(432, "Mollisols", 20, 0)
    assert result['beam']['dimensions_cm'] == "20x40"
    assert result['barrier']['depth_cm'] == 80
    assert result['drain']['diameter_in'] == 4
    assert "#4231" in str(result['sop_references'])
