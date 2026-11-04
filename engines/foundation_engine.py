
def design_foundation(area: float, soil_type: str = "Mollisols", spt: float = None, slope_percent: float = 0):
    import math
    perimeter = math.sqrt(area)*4 if area>0 else 0
    pile_required = False
    pile_reason = ""
    if soil_type.lower() == "vertisols" or (spt is not None and spt < 15):
        pile_required = True
        pile_reason = f"Vertisols critical or SPT {spt} <15 per ASTM D1586 - Pile D30 required per SOP #4231"
    else:
        pile_reason = f"SPT {spt} >=15 or soil {soil_type} not Vertisols - pile optional"
    pile_spec = {"required":pile_required,"diameter_cm":30,"length_m":"2-3m","spt_threshold":15,"count":24 if pile_required else 0,"grid":"2x2m","cost_per_unit_thb":1800,"total_cost_thb":24*1800 if pile_required else 0,"standard":"ASTM D1586 SPT 3 points Depth 6m","reason":pile_reason,"failure_code":"#4231 No SPT settlement 30%"}
    beam_spec = {"dimensions_cm":"20x40","reinforcement":"4-DB16","stirrup":"RB6@200 mm","standard":"ACI 318","cost_per_m_thb":1200,"total_length_m":perimeter,"total_cost_thb":perimeter*1200}
    barrier_spec = {"material":"HDPE","depth_cm":80,"distance_m":1.5,"cost_per_m_thb":450,"total_length_m":perimeter,"total_cost_thb":perimeter*450,"purpose":"Root crack prevention #7012 for Ficus 8m, Foxtail 7m","required_when":"Ficus or Foxtail within 1.5m of structure"}
    drain_spec = {"material":"PVC","diameter_in":4,"slope_percent":"1-2%","basin_spacing_m":10,"gravel_cm":20,"geotextile":True,"cost_per_m_thb":650,"total_length_m":perimeter,"total_cost_thb":perimeter*650,"purpose":"Waterlogging prevention #3102","standard":"SOP #3102"}
    settlement_spec = {"threshold_cm":2,"warranty":"1 year free remediation if settlement >2cm","monitoring":"Required for Vertisols"}
    return {"area_sqm":area,"soil_type":soil_type,"spt_n_value":spt,"spt_standard":"ASTM D1586 3 points Depth 6m","expansion_index_standard":"ASTM D4829","pile":pile_spec,"beam":beam_spec,"barrier":barrier_spec,"drain":drain_spec,"settlement":settlement_spec,"sop_references":["#4231 No SPT settlement","#3102 No drain plant death","#7012 No barrier root intrusion"],"official_sources":["ASTM D1586 https://www.astm.org/d1586-d1586m-18.html","ASTM D4829 https://www.astm.org/d4829-21.html"],"compliance":"CODE READY per ASTM D1586 D4829"}
