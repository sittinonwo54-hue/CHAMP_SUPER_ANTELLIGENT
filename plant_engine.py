"""CHAMP_SUPER_ANTELLIGENT - Plant Engine - CODE READY - 20 REAL species ONLY
500 = [DOCUMENTATION_ONLY] - Do NOT claim as CODE READY. 100 Projects = [DOCUMENTATION_ONLY]. 135 Agents = [DOCUMENTATION_ONLY]. Vector DB 384 dim = [DOCUMENTATION_ONLY].
"""
PLANTS_20 = [
    ("Heliconia rostrata", "Heliconia", "Vertisols tolerant"),
    ("Plumeria rubra", "Frangipani / Leelawadee", "Vertisols tolerant"),
    ("Bambusa vulgaris", "Bamboo / Clumping", "Vertisols tolerant - Barrier 80cm"),
    ("Sansevieria trifasciata", "Snake plant", "All soils - Root Barrier edge"),
    ("Cynodon dactylon", "Bermuda grass", "All soils"),
    ("Ophiopogon japonicus", "Mondo grass", "All soils"),
    ("Musa acuminata", "Banana", "Vertisols tolerant"),
    ("Tectona grandis", "Teak", "Mollisols"),
    ("Ficus benjamina", "Ficus", "Vertisols tolerant - Barrier 80cm Distance 1.5m"),
    ("Ficus microcarpa", "Ficus microcarpa", "Vertisols tolerant - Barrier 80cm"),
    ("Alpinia purpurata", "Red ginger", "Vertisols tolerant"),
    ("Strelitzia nicolai", "Traveller's Palm", "Vertisols tolerant"),
    ("Cordyline fruticosa", "Ti plant", "All soils"),
    ("Hibiscus rosa-sinensis", "Hibiscus", "All soils"),
    ("Ixora coccinea", "Ixora", "All soils"),
    ("Nelumbo nucifera", "Lotus", "Wet / Histosols"),
    ("Nymphaea spp.", "Water lily", "Wet"),
    ("Pandanus amaryllifolius", "Pandan", "Vertisols tolerant"),
    ("Curcuma longa", "Turmeric", "All soils"),
    ("Cymbopogon citratus", "Lemongrass", "All soils"),
]

def select_plants(soil_order, sun="full"):
    if soil_order == "Vertisols":
        return [p for p in PLANTS_20 if "Vertisols" in p[2] or "All soils" in p[2]]
    return PLANTS_20
