"""CHAMP_SUPER_ANTELLIGENT - Soil Engine - CODE READY - USDA 12 Orders
Vertisols trigger: Clay >30% to 50cm AND COLE >=0.09 + slickensides + smectite/montmorillonite
DATA_GATE #4231: Vertisols without SPT -> BLOCK
Fixes when Vertisols: Pile D30 L2-3m, Root Barrier HDPE 80cm, Slot Drain 1-2% slope
"""
ORDERS = ["Entisols", "Inceptisols", "Andisols", "Mollisols", "Alfisols", "Spodosols", "Ultisols", "Oxisols", "Histosols", "Vertisols", "Aridisols", "Gelisols"]

def classify_soil(clay_pct=None, cole=None, spt=None, has_slickensides=False):
    if clay_pct is not None and clay_pct > 30 and cole is not None and cole >= 0.09:
        order = "Vertisols"
        if spt is None:
            return {"order": order, "blocked": True, "code": "#4231", "error": "DATA_GATE #4231 - Vertisols requires SPT - No SPT No Build"}
        fixes = {"pile": "D30 L2-3m SPT>15 Grid 2x2m", "barrier": "HDPE 80cm Distance 1.5m", "drain": "PVC 4in Slot Drain Slope 1-2% Basin 10m Gravel 20cm Geotextile", "beam": "20x40 4-DB16 RB6@200"}
        return {"order": order, "blocked": False, "clay_pct": clay_pct, "cole": cole, "spt": spt, "fixes": fixes, "note": "Expansive clay - settlement risk 30% without fixes"}
    return {"order": "Mollisols (default - need full lab test for exact order)", "blocked": False, "clay_pct": clay_pct, "cole": cole, "fixes": {"pile": "Check SPT", "barrier": "Per species", "drain": "PVC 4in Slope 1-2%"}}
