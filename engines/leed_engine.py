
LEED_V5_CATEGORIES = {
    "IP":{"name":"Integrative Process","points":1,"max":1},
    "LT":{"name":"Location and Transportation","points":15,"max":15,"breakdown":"1+2+6+4+2 per official"},
    "SS":{"name":"Sustainable Sites","points":11,"max":11,"breakdown":"2+1+3+2+2+1 per official"},
    "WE":{"name":"Water Efficiency","points":9,"max":9,"breakdown":"1+8 per official"},
    "EA":{"name":"Energy and Atmosphere","points":33,"max":33,"breakdown":"5+5+10+5+4+2+2 per official"},
    "MR":{"name":"Materials and Resources","points":18,"max":18,"breakdown":"3+6+2+5+2 per official"},
    "EQ":{"name":"Indoor Environmental Quality / EQ","points":13,"max":13,"breakdown":"1+7+1+2+2 per official"},
    "PR":{"name":"Project Requirements / Innovation or Regional Priority","points":10,"max":10,"breakdown":"9+1 per official"},
}
TOTAL_POINTS=110
def calculate_leed(area: float = 100, soil_type: str = "Mollisols", plant_count: int = 5, material_sustainable: bool = True):
    score={}
    total=0
    score["IP"]=1; total+=1
    lt_score=10; score["LT"]=min(lt_score, LEED_V5_CATEGORIES["LT"]["max"]); total+=score["LT"]
    ss_score=6
    if soil_type.lower()=="vertisols": ss_score+=2
    score["SS"]=min(ss_score, LEED_V5_CATEGORIES["SS"]["max"]); total+=score["SS"]
    we_score=5
    if plant_count>=5: we_score+=2
    score["WE"]=min(we_score, LEED_V5_CATEGORIES["WE"]["max"]); total+=score["WE"]
    ea_score=20; score["EA"]=min(ea_score, LEED_V5_CATEGORIES["EA"]["max"]); total+=score["EA"]
    mr_score=10
    if material_sustainable: mr_score+=3
    score["MR"]=min(mr_score, LEED_V5_CATEGORIES["MR"]["max"]); total+=score["MR"]
    eq_score=8; score["EQ"]=min(eq_score, LEED_V5_CATEGORIES["EQ"]["max"]); total+=score["EQ"]
    pr_score=5; score["PR"]=min(pr_score, LEED_V5_CATEGORIES["PR"]["max"]); total+=score["PR"]
    total=min(total,TOTAL_POINTS)
    if total>=80: level="Platinum"
    elif total>=60: level="Gold"
    elif total>=50: level="Silver"
    elif total>=40: level="Certified"
    else: level="Not Certified"
    return {"total_points":total,"max_points":TOTAL_POINTS,"certification_level":level,"breakdown":score,"categories":LEED_V5_CATEGORIES,"official_source":"USGBC LEED v5 https://www.usgbc.org/leed/v5 - Official PDF Lines 136-290","status":"PARTIAL - structure CODE READY per USGBC PDF, calculation PARTIAL per reality check","notes":"LEED v5 110 Points IP1 LT15 SS11 WE9 EA33 MR18 EQ13 PR10 per canonical - PARTIAL implementation"}
