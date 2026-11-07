"""CHAMP_SUPER_ANTELLIGENT - ASTM Engine - CODE READY
SPT D1586: Hammer 63.5kg Drop 760mm Seating 150mm N = last 300mm
EI D4829: EI = 1000*(hf-hi)/hi. 0-20 Very Low, 21-50 Low, 51-90 Medium, 91-130 High, >130 Very High
"""
def spt_spec():
    return {"standard": "ASTM D1586", "hammer_kg": 63.5, "drop_mm": 760, "seating_mm": 150, "n_definition": "last 300mm", "required": "3 points Depth 6m", "pile_trigger": "SPT <15 -> Pile D30 L2-3m"}

def expansion_index(hi, hf):
    if hi is None or hi == 0:
        return {"error": "hi required"}
    ei = 1000 * (hf - hi) / hi
    if ei <= 20:
        lvl = "Very Low"
    elif ei <= 50:
        lvl = "Low"
    elif ei <= 90:
        lvl = "Medium"
    elif ei <= 130:
        lvl = "High"
    else:
        lvl = "Very High"
    return {"ei": round(ei, 1), "level": lvl, "standard": "ASTM D4829"}
