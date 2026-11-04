
import re
SANITIZE_PATTERN = re.compile(r'^[a-zA-Z0-9 _\-\.\(\)%]+$')
MAX_LENGTH = 100
def sanitize_input(value: str) -> str:
    if not isinstance(value, str): value = str(value)
    if len(value) > MAX_LENGTH: raise ValueError(f"Input exceeds max length {MAX_LENGTH}")
    if not SANITIZE_PATTERN.match(value): raise ValueError(f"Input contains invalid characters: {value}")
    return value.strip()
def validate_area(area):
    try: area_val = float(area)
    except (TypeError, ValueError): raise ValueError(f"Area must be numeric, got {area}")
    if area_val <= 0: return 0.0
    if area_val > 10000: raise ValueError(f"Area {area_val} exceeds maximum 10000 sqm")
    return area_val
def validate_spt(spt):
    if spt is None: raise ValueError("DATA_GATE #4231: SPT is mandatory for Vertisols - No SPT No build")
    try: spt_val = float(spt)
    except (TypeError, ValueError): raise ValueError(f"SPT must be numeric, got {spt}")
    if spt_val < 0 or spt_val > 50: raise ValueError(f"SPT {spt_val} out of range 0-50 per ASTM D1586")
    return spt_val
def validate_landscape_input(data: dict):
    errors=[]; normalized={}
    try:
        area_raw = data.get('area', data.get('area_sqm',0))
        normalized['area']=validate_area(area_raw)
    except Exception as e:
        errors.append(f"AREA_ERROR: {str(e)}"); normalized['area']=0.0
    soil_type = data.get('soil_type', data.get('soil','Mollisols'))
    try:
        if isinstance(soil_type,str): sanitize_input(soil_type)
        normalized['soil_type']=soil_type
    except Exception as e:
        errors.append(f"SOIL_ERROR: {str(e)}"); normalized['soil_type']='Mollisols'
    try:
        slope = float(data.get('slope_percent', data.get('slope',0)))
        normalized['slope_percent']=slope
    except: normalized['slope_percent']=0.0
    access = data.get('access_type', data.get('access','normal'))
    try:
        if isinstance(access,str): sanitize_input(access)
        normalized['access_type']=access
    except Exception as e:
        errors.append(f"ACCESS_ERROR: {str(e)}"); normalized['access_type']='normal'
    spt_raw = data.get('spt', data.get('spt_n_value'))
    if spt_raw is None:
        if str(normalized.get('soil_type','')).lower()=='vertisols':
            errors.append("DATA_GATE #4231: SPT is mandatory for Vertisols - No SPT No build - Settlement risk 30% per SOP #4231")
            normalized['spt']=None
        else:
            normalized['spt']=None
    else:
        try: normalized['spt']=validate_spt(spt_raw)
        except Exception as e: errors.append(f"SPT_ERROR: {str(e)}"); normalized['spt']=None
    try:
        pile_count=int(data.get('pile_count',24))
        normalized['pile_count']=pile_count
    except: normalized['pile_count']=24
    has_data_gate_error = any("DATA_GATE #4231" in e for e in errors)
    if has_data_gate_error: valid=False
    elif normalized['area']<=0:
        valid=False
        if not errors: errors.append("AREA_ERROR: Area must be >0")
    else:
        valid=len(errors)==0
    return valid, normalized, errors
