"""CHAMP_SUPER_ANTELLIGENT - SOP Engine - 45 Days 13 Phases - Planning target, not guarantee
SOP 45 Days Gantt 13 Phases = [DOCUMENTATION_ONLY] for Gantt engine - sequence below is real landscape construction sequence.
"""
PHASES_13 = [
    (1, "Days 1-3", "Survey + SPT 3 points Depth 6m + Soil test"),
    (2, "Days 4-5", "Design Master Plan 1:100 8 Points + Section A-A"),
    (3, "Days 6-7", "BOQ + Approval"),
    (4, "Days 8-10", "Site clearance + Topsoil"),
    (5, "Days 11-15", "Pile D30 L2-3m + Beam 20x40"),
    (6, "Days 16-18", "Root Barrier HDPE 80cm"),
    (7, "Days 19-22", "Slot Drain PVC 4in Slope 1-2%"),
    (8, "Days 23-28", "Hardscape Travertine / Slate"),
    (9, "Days 29-33", "Soil improvement + Planting 20 species"),
    (10, "Days 34-37", "Irrigation + Lighting"),
    (11, "Days 38-40", "Finishing + Cleaning"),
    (12, "Days 41-43", "Inspection + Punch list"),
    (13, "Days 44-45", "Handover + Warranty 1 year subsidence"),
]

def get_sop():
    return PHASES_13
