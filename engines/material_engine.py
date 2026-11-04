
MATERIAL_PALETTE = [
    {"id":"MAT_001","name":"Travertine 60x60","type":"Hardscape","unit":"sqm","price_thb_per_unit":850,"thai_market":"2024-2025","spec":"60x60 cm","notes":"Hardscape material - Thai market 2024-2025"},
    {"id":"MAT_002","name":"Black Slate","type":"Hardscape","unit":"sqm","price_thb_per_unit":1200,"thai_market":"2024-2025","spec":"Natural slate","notes":"Hardscape material"},
    {"id":"MAT_003","name":"Charcoal Gravel / Charcoal stone","type":"Hardscape","unit":"sqm","price_thb_per_unit":450,"thai_market":"2024-2025","spec":"Charcoal stone","notes":"Hardscape material"},
    {"id":"MAT_004","name":"Brass strip 10mm","type":"Divider","unit":"m","price_thb_per_unit":3500,"thai_market":"2024-2025","spec":"10mm brass","notes":"Divider strip"},
    {"id":"MAT_005","name":"Topsoil removal 20cm","type":"Earthwork","unit":"sqm","price_thb_per_unit":50,"soil_multiplier":"All 1.0","notes":"SOP for surface preparation"},
    {"id":"MAT_006","name":"O Horizon removal Histosols organic 40-300cm","type":"Earthwork","unit":"sqm","price_thb_per_unit":150,"soil_multiplier":"Histosols 1.5","notes":"Settlement control 50% for organic layer"},
]
def get_material_palette(area: float = None, include_pricing: bool = True):
    total_cost=0
    if area:
        for mat in MATERIAL_PALETTE:
            if mat["unit"]=="sqm":
                mat["estimated_qty"]=area*0.5
                mat["estimated_cost"]=mat["estimated_qty"]*mat["price_thb_per_unit"]
                total_cost+=mat["estimated_cost"]
    return {"materials":MATERIAL_PALETTE,"count":len(MATERIAL_PALETTE),"thai_market":"2024-2025","total_estimated_cost_thb":round(total_cost,2) if area else 0,"notes":"Material palette CODE READY but pricing DOCUMENTATION ONLY quarterly update per reality check","official_source":"Thai Market 2024-2025 suppliers","claim":"BOQ 100 Items PARTIAL - sample 5-10 items actual, 90 additional DOCUMENTATION ONLY","pricing_status":"PARTIAL - Thai market 2024-2025 sample"}
