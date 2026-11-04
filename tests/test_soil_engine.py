
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engines.soil_engine import classify_soil, get_all_usda_orders, USDA_ORDERS

def test_12_usda_orders():
    orders = get_all_usda_orders()
    assert len(orders) == 12
    assert "Vertisols" in orders
    assert "Mollisols" in orders

def test_classify_vertisols():
    result = classify_soil("Vertisols", 8)
    assert result['soil_order'] == "Vertisols"
    assert result['is_usda_order'] == True
    assert result['soil_mult'] == 1.5
    assert result['spt_required'] == True

def test_classify_mollisols():
    result = classify_soil("Mollisols", 20)
    assert result['soil_mult'] == 1.1

def test_vertisols_extent_335M_ha():
    result = classify_soil("Vertisols")
    assert "335M" in result['vertisols_extent']
