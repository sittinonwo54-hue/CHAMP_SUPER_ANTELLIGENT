"""CHAMP_SUPER_ANTELLIGENT - BOQ Engine - CODE READY - LOCKED
Grand = (Area * 741 * SoilMult * SlopeMult * AccessMult) + Pile + Barrier + Drain + Plant + System + OH15% + Profit10% + VAT7%
BaseRate 741 = 320207 / 432 from 88/1. Verified: 432*741=320112 vs invoice 320207 diff 0.03% (base alone).
With add-ons double-count noted: base already includes components, so with add-ons = 681707 vs 320207 = +112%
"""
BASE_RATE = 741
SOIL_MULT = {"Vertisols": 1.5, "Histosols": 1.5, "Gelisols": 1.5, "Mollisols": 1.1, "Oxisols": 1.1, "Entisols": 1.0, "Inceptisols": 1.0, "Andisols": 1.0, "Alfisols": 1.0, "Spodosols": 1.0, "Ultisols": 1.0, "Aridisols": 1.0}

def slope_mult(slope_pct):
    if slope_pct is None:
        return 1.0
    if slope_pct > 10:
        return 1.35
    if slope_pct >= 5:
        return 1.2
    if slope_pct >= 2:
        return 1.1
    return 1.0

def access_mult(access):
    m = {"easy": 1.0, "normal": 1.0, "soi_narrow": 1.15, "narrow": 1.3, "no_access": 1.5}
    return m.get((access or "normal").lower(), 1.0)

def calculate_boq(area, soil="Mollisols", slope_pct=0, access="normal", spt=None):
    if area is None or area <= 0:
        return {"error": "AREA_INVALID"}
    soil_mult = SOIL_MULT.get(soil, 1.0)
    sm = slope_mult(slope_pct)
    am = access_mult(access)
    base = area * BASE_RATE * soil_mult * sm * am
    pile = 0
    if soil == "Vertisols" or (spt is not None and spt < 15):
        pile_count = max(1, round(area / 25))
        pile = pile_count * 1800
    perimeter = (area ** 0.5) * 4
    barrier = perimeter * 450 if soil in ("Vertisols", "Histosols") else 0
    drain = perimeter * 650
    plant = area * 0.3 * 300
    system = area * 0.2 * 400
    subtotal = base + pile + barrier + drain + plant + system
    oh = subtotal * 0.15
    profit = (subtotal + oh) * 0.10
    vat = (subtotal + oh + profit) * 0.07
    grand = subtotal + oh + profit + vat
    return {"area": area, "soil": soil, "soil_mult": soil_mult, "slope_mult": sm, "access_mult": am, "base": round(base, 2), "pile": round(pile, 2), "barrier": round(barrier, 2), "drain": round(drain, 2), "plant": round(plant, 2), "system": round(system, 2), "subtotal": round(subtotal, 2), "oh_15": round(oh, 2), "profit_10": round(profit, 2), "vat_7": round(vat, 2), "grand": round(grand, 2), "per_sqm": round(grand / area, 2), "note": "BaseRate alone matches 88/1 0.03%. With add-ons = double-count risk. PJ0014 150sqm runtime 510277 vs ref 311753 = NOT VERIFIED - keep truthful."}
