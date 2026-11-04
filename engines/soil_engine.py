
USDA_ORDERS = ["Alfisols","Andisols","Aridisols","Entisols","Gelisols","Histosols","Inceptisols","Mollisols","Oxisols","Spodosols","Ultisols","Vertisols"]
WRB_GROUPS = ["Acrisols","Alisols","Albeluvisols","Andosols","Anthrosols","Arenosols","Calcisols","Cambisols","Chernozems","Cryosols","Durisols","Ferralsols","Fluvisols","Gleysols","Gypsisols","Histosols","Kastanozems","Leptosols","Lixisols","Luvisols","Nitisols","Phaeozems","Planosols","Plinthosols","Podzols","Regosols","Solonchaks","Solonetz","Stagnosols","Umbrisols","Vertisols","Technosols"]
HORIZONS = {"O":"Organic layer 40-300cm Histosols","A":"Topsoil","E":"Eluvial horizon","B":"Subsoil","C":"Parent material","R":"Bedrock"}
SOIL_CHARACTERISTICS = {
    "Vertisols": {"description":"Clay-rich soils shrink swell 335M ha global per FAO 308.5 Mha 2.36%","soil_mult":1.5,"risk_level":"Critical - Settlement 30% without SPT per #4231","distribution_ha":"335M ha global","spt_required":True,"foundation_required":"Pile D30 L2-3m SPT>15"},
    "Histosols": {"description":"Organic soils 40-300cm","soil_mult":1.5,"risk_level":"Critical","spt_required":True},
    "Gelisols": {"description":"Permafrost","soil_mult":1.5,"risk_level":"High","spt_required":True},
    "Entisols": {"description":"Young soils","soil_mult":1.0,"risk_level":"Low-Medium","spt_required":False},
    "Mollisols": {"description":"Grassland fertile base for 88/1 432sqm","soil_mult":1.1,"risk_level":"Low","spt_required":False},
    "Alfisols": {"soil_mult":1.2,"risk_level":"Medium","spt_required":False},
    "Andisols": {"soil_mult":1.2,"risk_level":"Medium","spt_required":False},
    "Aridisols": {"soil_mult":1.0,"risk_level":"Low","spt_required":False},
    "Inceptisols": {"soil_mult":1.1,"risk_level":"Low-Medium","spt_required":False},
    "Oxisols": {"soil_mult":1.0,"risk_level":"Low","spt_required":False},
    "Spodosols": {"soil_mult":1.0,"risk_level":"Low","spt_required":False},
    "Ultisols": {"soil_mult":1.2,"risk_level":"Medium","spt_required":False},
}
def classify_soil(soil_type: str, spt: float = None):
    soil_type_clean = str(soil_type).strip().capitalize()
    for order in USDA_ORDERS:
        if order.lower() == soil_type_clean.lower():
            soil_type_clean = order
            break
    if soil_type_clean not in USDA_ORDERS:
        for wrb in WRB_GROUPS:
            if wrb.lower() == soil_type_clean.lower():
                soil_type_clean = wrb
                break
    char = SOIL_CHARACTERISTICS.get(soil_type_clean, {"description":f"{soil_type_clean}","soil_mult":1.0,"risk_level":"Unknown","spt_required":False})
    return {"soil_order":soil_type_clean,"is_usda_order":soil_type_clean in USDA_ORDERS,"is_wrb_group":soil_type_clean in WRB_GROUPS,"usda_orders_total":12,"wrb_groups_total":32,"horizons":HORIZONS,"characteristics":char,"soil_mult":char.get("soil_mult",1.0),"risk_level":char.get("risk_level","Unknown"),"spt_required":char.get("spt_required",False),"spt_value":spt,"data_gate_4231":"SPT mandatory for Vertisols" if soil_type_clean=="Vertisols" else "SPT recommended","official_sources":["USDA https://www.nrcs.usda.gov","FAO WRB https://www.fao.org/soils-portal"],"vertisols_extent":"335M ha global per FAO, 308.5 Mha 2.36% per FAO-UNESCO, 80M Australia 73M India 56M Sudan"}
def get_all_usda_orders(): return USDA_ORDERS
def get_all_wrb_groups(): return WRB_GROUPS
