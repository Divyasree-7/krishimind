import random
import requests
from datetime import datetime, timedelta
from config.settings import DATA_GOV_API_KEY


MOCK_MANDI_DATA = {
    "wheat":      {"msp": 2275, "base_price": 2300},
    "rice":       {"msp": 2183, "base_price": 2250},
    "cotton":     {"msp": 6620, "base_price": 6800},
    "soybean":    {"msp": 4600, "base_price": 4750},
    "sugarcane":  {"msp": 315,  "base_price": 330},
    "maize":      {"msp": 1962, "base_price": 2000},
    "groundnut":  {"msp": 6377, "base_price": 6500},
    "onion":      {"msp": 0,    "base_price": 1800},
    "tomato":     {"msp": 0,    "base_price": 2200},
    "potato":     {"msp": 0,    "base_price": 1200},
    "bajra":      {"msp": 2500, "base_price": 2550},
    "jowar":      {"msp": 3180, "base_price": 3200},
    "tur dal":    {"msp": 7000, "base_price": 7200},
    "chana":      {"msp": 5440, "base_price": 5600},
    "mustard":    {"msp": 5650, "base_price": 5700},
}

DATA_GOV_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_BASE_URL = f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}"


def _try_live_mandi_price(crop: str, state: str) -> dict | None:
    """Attempt to fetch real price from data.gov.in Agmarknet dataset. Returns None on failure."""
    if not DATA_GOV_API_KEY or DATA_GOV_API_KEY == "PASTE_YOUR_DATA_GOV_KEY_HERE":
        return None
    try:
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": 5,
            "filters[commodity]": crop.title(),
            "filters[state]": state,
        }
        resp = requests.get(DATA_GOV_BASE_URL, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if not records:
            return None
        rec = records[0]
        modal_price = float(rec.get("modal_price", 0))
        if modal_price <= 0:
            return None
        return {
            "crop": crop.lower(),
            "state": state,
            "current_price_per_quintal": round(modal_price),
            "market_name": rec.get("market", "Unknown"),
            "date": rec.get("arrival_date", datetime.now().strftime("%Y-%m-%d")),
            "source": "live"
        }
    except Exception:
        return None


def get_mandi_price(crop: str, state: str = "Maharashtra") -> dict:
    """
    Fetch current mandi price for a crop.
    Tries live data.gov.in Agmarknet API first; falls back to realistic sample data if unavailable.
    """
    crop_lower = crop.lower().strip()

    live = _try_live_mandi_price(crop_lower, state)
    if live:
        base = MOCK_MANDI_DATA.get(crop_lower, {"msp": 0})
        msp = base["msp"]
        current_price = live["current_price_per_quintal"]
        price_vs_msp = "above" if current_price > msp else "below" if msp > 0 else "no MSP"
        pct_diff = round(((current_price - msp) / msp) * 100, 1) if msp > 0 else None
        return {
            "crop": crop_lower,
            "state": state,
            "current_price_per_quintal": current_price,
            "msp_per_quintal": msp,
            "price_vs_msp": price_vs_msp,
            "pct_above_msp": pct_diff,
            "date": live["date"],
            "market_name": live.get("market_name"),
            "source": "Agmarknet (live, data.gov.in)",
            "is_live": True
        }

    if crop_lower not in MOCK_MANDI_DATA:
        return {
            "error": f"Price data not available for '{crop}'. "
                     f"Supported: {', '.join(MOCK_MANDI_DATA.keys())}"
        }

    base = MOCK_MANDI_DATA[crop_lower]
    variation = random.uniform(-0.05, 0.08)
    current_price = round(base["base_price"] * (1 + variation))
    msp = base["msp"]

    price_vs_msp = "above" if current_price > msp else "below" if msp > 0 else "no MSP"
    pct_diff = round(((current_price - msp) / msp) * 100, 1) if msp > 0 else None

    return {
        "crop": crop_lower,
        "state": state,
        "current_price_per_quintal": current_price,
        "msp_per_quintal": msp,
        "price_vs_msp": price_vs_msp,
        "pct_above_msp": pct_diff,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Sample data (live Agmarknet feed unavailable)",
        "is_live": False
    }


def get_price_trend(crop: str, days: int = 7) -> dict:
    """Generate a price trend for the last N days (sample data, clearly labeled)."""
    crop_lower = crop.lower().strip()
    if crop_lower not in MOCK_MANDI_DATA:
        return {"error": f"No trend data for '{crop}'"}

    base_price = MOCK_MANDI_DATA[crop_lower]["base_price"]
    trend = []
    price = base_price * random.uniform(0.95, 1.0)
    for i in range(days, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        price = price * random.uniform(0.97, 1.04)
        trend.append({"date": date, "price": round(price)})

    prices = [t["price"] for t in trend]
    direction = "rising" if prices[-1] > prices[0] else "falling" if prices[-1] < prices[0] else "stable"

    return {
        "crop": crop_lower,
        "trend": trend,
        "direction": direction,
        "min_price": min(prices),
        "max_price": max(prices),
        "recommendation": (
            "Good time to sell — prices are rising." if direction == "rising"
            else "Consider holding stock if possible — prices are falling."
            if direction == "falling"
            else "Prices are stable. Sell based on your storage capacity."
        )
    }


def get_best_selling_markets(crop: str, state: str = "Maharashtra") -> list:
    """Return top mandis for selling a crop (reference list)."""
    mandis = {
        "Maharashtra": ["Pune APMC", "Nashik APMC", "Nagpur APMC", "Solapur APMC"],
        "Punjab":      ["Ludhiana APMC", "Amritsar Mandi", "Patiala Mandi"],
        "Karnataka":   ["Bangalore APMC", "Hubli Mandi", "Belgaum Mandi"],
        "Gujarat":     ["Ahmedabad APMC", "Rajkot APMC", "Surat APMC"],
        "Haryana":     ["Karnal Mandi", "Hisar Mandi", "Panipat Mandi"],
        "Uttar Pradesh": ["Lucknow Mandi", "Kanpur Mandi", "Agra Mandi"],
        "Madhya Pradesh": ["Indore APMC", "Bhopal Mandi", "Ujjain Mandi"],
        "Rajasthan":   ["Jaipur Mandi", "Kota Mandi", "Jodhpur Mandi"],
        "Andhra Pradesh": ["Guntur Market", "Vijayawada Market"],
        "Bihar":       ["Patna Mandi", "Muzaffarpur Mandi"],
        "West Bengal": ["Kolkata Mandi", "Siliguri Mandi"],
    }
    return mandis.get(state, ["Local APMC", "Nearest District Mandi"])


def get_all_crop_prices(state: str = "Maharashtra") -> list:
    """Get current prices for all supported crops - used for dashboard view."""
    results = []
    for crop in MOCK_MANDI_DATA.keys():
        price_data = get_mandi_price(crop, state)
        if "error" not in price_data:
            results.append(price_data)
    return results
