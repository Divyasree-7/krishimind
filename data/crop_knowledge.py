CROP_KNOWLEDGE_BASE = {
    "wheat": {
        "season": "rabi",
        "sowing_months": ["November", "December"],
        "harvest_months": ["March", "April"],
        "soil_types": ["loamy", "clay loam", "alluvial"],
        "water_requirement": "medium",
        "states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"],
        "common_pests": ["aphids", "rust", "powdery mildew"],
        "tips": "Ensure timely irrigation at crown root initiation stage."
    },
    "rice": {
        "season": "kharif",
        "sowing_months": ["June", "July"],
        "harvest_months": ["October", "November"],
        "soil_types": ["clay", "clay loam", "alluvial"],
        "water_requirement": "high",
        "states": ["West Bengal", "Uttar Pradesh", "Punjab", "Andhra Pradesh", "Odisha"],
        "common_pests": ["brown planthopper", "stem borer", "blast disease"],
        "tips": "Transplant 21-day-old seedlings for best yields."
    },
    "cotton": {
        "season": "kharif",
        "sowing_months": ["May", "June"],
        "harvest_months": ["October", "November", "December"],
        "soil_types": ["black cotton soil", "deep alluvial"],
        "water_requirement": "medium",
        "states": ["Gujarat", "Maharashtra", "Telangana", "Punjab", "Haryana"],
        "common_pests": ["bollworm", "whitefly", "aphids", "pink bollworm"],
        "tips": "Use Bt cotton varieties for better bollworm resistance."
    },
    "soybean": {
        "season": "kharif",
        "sowing_months": ["June", "July"],
        "harvest_months": ["September", "October"],
        "soil_types": ["well-drained loamy", "black soil"],
        "water_requirement": "medium",
        "states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka"],
        "common_pests": ["girdle beetle", "stem fly", "yellow mosaic virus"],
        "tips": "Inoculate seeds with Rhizobium culture before sowing."
    },
    "onion": {
        "season": "rabi",
        "sowing_months": ["October", "November"],
        "harvest_months": ["February", "March", "April"],
        "soil_types": ["well-drained sandy loam", "medium loam"],
        "water_requirement": "medium",
        "states": ["Maharashtra", "Karnataka", "Madhya Pradesh", "Gujarat"],
        "common_pests": ["thrips", "purple blotch", "basal rot"],
        "tips": "Stop irrigation 10 days before harvest to improve shelf life."
    },
    "tomato": {
        "season": "all seasons",
        "sowing_months": ["June", "July", "October", "November"],
        "harvest_months": ["varies by sowing"],
        "soil_types": ["well-drained sandy loam", "loamy"],
        "water_requirement": "medium-high",
        "states": ["Andhra Pradesh", "Karnataka", "Maharashtra", "Odisha"],
        "common_pests": ["fruit borer", "early blight", "late blight", "whitefly"],
        "tips": "Use drip irrigation and mulching to reduce disease incidence."
    },
    "maize": {
        "season": "kharif",
        "sowing_months": ["June", "July"],
        "harvest_months": ["September", "October"],
        "soil_types": ["well-drained loamy", "sandy loam"],
        "water_requirement": "medium",
        "states": ["Karnataka", "Andhra Pradesh", "Bihar", "Uttar Pradesh"],
        "common_pests": ["fall armyworm", "stem borer", "leaf blight"],
        "tips": "Apply nitrogen in splits — 1/3 at sowing, 1/3 at knee height, 1/3 at tasseling."
    },
    "groundnut": {
        "season": "kharif",
        "sowing_months": ["June", "July"],
        "harvest_months": ["October", "November"],
        "soil_types": ["sandy loam", "red loamy"],
        "water_requirement": "medium",
        "states": ["Gujarat", "Andhra Pradesh", "Rajasthan", "Tamil Nadu"],
        "common_pests": ["leaf miner", "tikka disease", "stem rot"],
        "tips": "Gypsum application at pegging stage improves pod filling."
    },
    "potato": {
        "season": "rabi",
        "sowing_months": ["October", "November"],
        "harvest_months": ["January", "February"],
        "soil_types": ["sandy loam", "loamy"],
        "water_requirement": "medium",
        "states": ["Uttar Pradesh", "West Bengal", "Punjab", "Bihar"],
        "common_pests": ["late blight", "early blight", "aphids", "cut worm"],
        "tips": "Use certified seed potato and maintain proper earthing up."
    },
    "mustard": {
        "season": "rabi",
        "sowing_months": ["October", "November"],
        "harvest_months": ["February", "March"],
        "soil_types": ["loamy", "sandy loam", "alluvial"],
        "water_requirement": "low-medium",
        "states": ["Rajasthan", "Uttar Pradesh", "Haryana", "Madhya Pradesh"],
        "common_pests": ["aphids", "painting bug", "alternaria blight"],
        "tips": "One irrigation at flowering stage is critical for yield."
    }
}


def get_crop_info(crop: str) -> dict:
    return CROP_KNOWLEDGE_BASE.get(crop.lower().strip(), {})


def recommend_crops_for_context(soil_type: str, season: str, state: str) -> list:
    """Return a list of suitable crops for given soil, season, and state."""
    suitable = []
    for crop, info in CROP_KNOWLEDGE_BASE.items():
        season_match = season.lower() in info["season"].lower() or info["season"] == "all seasons"
        soil_match = any(soil_type.lower() in s for s in info["soil_types"])
        state_match = state in info.get("states", [])
        if season_match and (soil_match or state_match):
            suitable.append(crop)
    return suitable
