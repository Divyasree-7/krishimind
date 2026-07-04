PEST_RISK_DATABASE = {
    "kharif": {
        "cotton": [
            {"pest": "Pink Bollworm", "risk": "HIGH", "months": ["August", "September", "October"],
             "symptoms": "Entry holes in bolls, pink-colored larvae inside.",
             "prevention": "Use pheromone traps, Bt cotton varieties, early sowing."},
            {"pest": "Whitefly", "risk": "HIGH", "months": ["July", "August", "September"],
             "symptoms": "Yellowing leaves, sticky honeydew, sooty mold.",
             "prevention": "Spray neem-based pesticides, avoid excess nitrogen."},
        ],
        "rice": [
            {"pest": "Brown Planthopper", "risk": "HIGH", "months": ["August", "September"],
             "symptoms": "Hopper burn — circular brown patches in field.",
             "prevention": "Avoid excess nitrogen, use resistant varieties, drain fields periodically."},
            {"pest": "Stem Borer", "risk": "MEDIUM", "months": ["July", "August"],
             "symptoms": "Dead heart in vegetative stage, white ear in reproductive stage.",
             "prevention": "Remove egg masses, use Trichogramma cards."},
        ],
        "soybean": [
            {"pest": "Girdle Beetle", "risk": "HIGH", "months": ["July", "August"],
             "symptoms": "Girdling of stems, wilting of plant parts.",
             "prevention": "Deep summer ploughing, early sowing, apply recommended insecticides."},
            {"pest": "Yellow Mosaic Virus", "risk": "HIGH", "months": ["July", "August", "September"],
             "symptoms": "Yellow mosaic pattern on leaves, stunted growth.",
             "prevention": "Control whitefly (vector), use resistant varieties."},
        ],
        "maize": [
            {"pest": "Fall Armyworm", "risk": "HIGH", "months": ["June", "July", "August"],
             "symptoms": "Ragged leaf feeding, entry holes in whorl, sawdust-like frass.",
             "prevention": "Apply sand+lime mixture in whorl, use Spodoptera NPV."},
        ]
    },
    "rabi": {
        "wheat": [
            {"pest": "Yellow Rust", "risk": "HIGH", "months": ["January", "February"],
             "symptoms": "Yellow-orange pustules in stripes on leaves.",
             "prevention": "Use resistant varieties, apply Propiconazole at first sign."},
            {"pest": "Aphids", "risk": "MEDIUM", "months": ["January", "February", "March"],
             "symptoms": "Yellowing, honeydew deposits on leaves and grain.",
             "prevention": "Natural enemies (ladybird beetles), spray when threshold crossed."},
        ],
        "mustard": [
            {"pest": "Aphids", "risk": "HIGH", "months": ["December", "January", "February"],
             "symptoms": "Clusters on shoot tips, yellowing, reduced flowering.",
             "prevention": "Spray Thiamethoxam or Imidacloprid at threshold (101 aphids/plant)."},
            {"pest": "Alternaria Blight", "risk": "MEDIUM", "months": ["February", "March"],
             "symptoms": "Brown circular spots with concentric rings on leaves.",
             "prevention": "Spray Mancozeb or Iprodione at 50% flowering."},
        ],
        "potato": [
            {"pest": "Late Blight", "risk": "HIGH", "months": ["December", "January"],
             "symptoms": "Water-soaked lesions on leaves, white fungal growth below.",
             "prevention": "Spray Mancozeb preventively, use certified seed, avoid overhead irrigation."},
        ],
        "onion": [
            {"pest": "Thrips", "risk": "HIGH", "months": ["January", "February", "March"],
             "symptoms": "Silver streaks on leaves, leaf tip drying.",
             "prevention": "Spray Fipronil or Spinosad, use blue sticky traps."},
        ]
    }
}


def get_pest_risks(crop: str, season: str, month: str = None) -> list:
    """Get pest risks for a given crop and season."""
    season_lower = season.lower()
    crop_lower = crop.lower().strip()
    season_data = PEST_RISK_DATABASE.get(season_lower, {})
    pests = season_data.get(crop_lower, [])
    if month:
        pests = [p for p in pests if month in p.get("months", [])]
    return pests


def get_general_pest_alert(season: str, month: str) -> str:
    """Generate a general seasonal pest alert."""
    alerts = {
        "June":    "Kharif season starting — prepare fields, check for soil pests before sowing.",
        "July":    "Monsoon active — watch for fungal diseases and sucking pests.",
        "August":  "Peak pest pressure month — scout fields twice a week.",
        "September": "Bollworm and armyworm pressure high in cotton and maize.",
        "October": "Rabi preparation — treat soil for white grubs and termites.",
        "November": "Rabi sown — watch for aphids and rust in wheat and mustard.",
        "December": "Cool weather — late blight risk in potato, aphids in mustard.",
        "January":  "Rust season for wheat — apply fungicide preventively.",
        "February": "Aphid peak in mustard — monitor daily and spray at threshold.",
        "March":    "Harvest approaching — minimal spray to avoid residues.",
        "April":    "Zaid crops — check for mites and sucking pests in dry heat.",
        "May":      "Pre-kharif — deep plough to destroy overwintering pests.",
    }
    return alerts.get(month, "Scout your field regularly and maintain field hygiene.")
