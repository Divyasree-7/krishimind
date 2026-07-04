from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import os
import traceback

app = FastAPI(title="KrishiMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = None
init_error = None
try:
    from agents.orchestrator import OrchestratorAgent
    orchestrator = OrchestratorAgent()
except Exception as e:
    init_error = str(e)
    print(f"\n[STARTUP ERROR] Failed to initialize agents: {init_error}\n")

from tools.weather_tools import get_weather_forecast, compute_rainfall_risk
from tools.market_tools import get_mandi_price, get_price_trend, get_best_selling_markets, get_all_crop_prices
from data.crop_knowledge import get_crop_info, recommend_crops_for_context, CROP_KNOWLEDGE_BASE
from data.pest_data import get_pest_risks, get_general_pest_alert, PEST_RISK_DATABASE
from config.settings import DEFAULT_LOCATION, SEASONS


# ===================== CHAT =====================

class ChatRequest(BaseModel):
    message: str
    state: str = "Maharashtra"
    soil_type: str = "loamy"
    season: str = "kharif"
    crop: str = ""
    language: str = "auto"


class ChatResponse(BaseModel):
    response: str
    agents_used: list


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if orchestrator is None:
        raise HTTPException(status_code=503, detail=f"Server failed to start: {init_error}")
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    context = {
        "state": req.state,
        "soil_type": req.soil_type,
        "season": req.season,
        "crop": req.crop if req.crop.strip() else None,
        "language": req.language,
        "location": None
    }
    try:
        result = orchestrator.run(req.message, context)
        return ChatResponse(response=result["final_response"], agents_used=result["agents_used"])
    except Exception as e:
        print(f"[CHAT ERROR] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    if orchestrator is None:
        return {"status": "error", "detail": init_error}
    return {"status": "ok"}


# ===================== WEATHER DASHBOARD =====================

@app.get("/api/weather")
def weather_dashboard(lat: float = None, lon: float = None, name: str = None):
    latitude = lat if lat is not None else DEFAULT_LOCATION["latitude"]
    longitude = lon if lon is not None else DEFAULT_LOCATION["longitude"]
    location_name = name or DEFAULT_LOCATION["name"]

    forecast = get_weather_forecast(latitude, longitude)
    if "error" in forecast:
        raise HTTPException(status_code=502, detail=forecast["error"])

    risk = compute_rainfall_risk(forecast)
    daily = forecast.get("daily", {})
    current = forecast.get("current_weather", {})

    days = []
    dates = daily.get("time", [])
    for i in range(min(7, len(dates))):
        days.append({
            "date": dates[i],
            "max_temp": daily.get("temperature_2m_max", [None]*7)[i],
            "min_temp": daily.get("temperature_2m_min", [None]*7)[i],
            "rain_mm": daily.get("precipitation_sum", [None]*7)[i],
            "rain_prob": daily.get("precipitation_probability_max", [None]*7)[i],
            "wind_kmh": daily.get("windspeed_10m_max", [None]*7)[i],
            "weather_code": daily.get("weathercode", [None]*7)[i],
        })

    return {
        "location": location_name,
        "current_temp": current.get("temperature"),
        "current_wind": current.get("windspeed"),
        "risk_level": risk["risk_level"],
        "risk_message": risk["message"],
        "total_rain_mm": risk["total_expected_rain_mm"],
        "rain_probability_pct": risk["avg_rain_probability_pct"],
        "days": days
    }


# ===================== CROP CALENDAR =====================

@app.get("/api/crop-calendar")
def crop_calendar(crop: str = None, soil_type: str = "loamy", season: str = "kharif", state: str = "Maharashtra"):
    if crop:
        info = get_crop_info(crop)
        if not info:
            raise HTTPException(status_code=404, detail=f"No data for crop '{crop}'")
        return {"crop": crop.lower(), **info}

    suggested = recommend_crops_for_context(soil_type, season, state)
    results = []
    for c in suggested:
        info = get_crop_info(c)
        if info:
            results.append({"crop": c, **info})
    return {"suggested_crops": results}


@app.get("/api/crops/all")
def all_crops():
    return {"crops": list(CROP_KNOWLEDGE_BASE.keys())}


# ===================== MARKET DASHBOARD =====================

@app.get("/api/market/price")
def market_price(crop: str, state: str = "Maharashtra"):
    price = get_mandi_price(crop, state)
    if "error" in price:
        raise HTTPException(status_code=404, detail=price["error"])
    trend = get_price_trend(crop)
    markets = get_best_selling_markets(crop, state)
    return {"price": price, "trend": trend, "best_markets": markets}


@app.get("/api/market/overview")
def market_overview(state: str = "Maharashtra"):
    prices = get_all_crop_prices(state)
    return {"state": state, "crops": prices}


# ===================== PEST ALERTS =====================

@app.get("/api/pest-alerts")
def pest_alerts(season: str = None, month: str = None, state: str = "Maharashtra"):
    current_month = month or datetime.now().strftime("%B")
    if not season:
        season = "kharif"
        for s, months in SEASONS.items():
            if current_month in months:
                season = s
                break

    general_alert = get_general_pest_alert(season, current_month)
    season_data = PEST_RISK_DATABASE.get(season, {})

    alerts = []
    for crop, pests in season_data.items():
        for pest in pests:
            if current_month in pest.get("months", []):
                alerts.append({"crop": crop, **pest})

    return {
        "season": season,
        "month": current_month,
        "general_alert": general_alert,
        "active_alerts": alerts
    }


# ===================== SERVE FRONTEND =====================

web_dir = os.path.join(os.path.dirname(__file__), "web")
app.mount("/", StaticFiles(directory=web_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 50)
    print("Starting KrishiMind server...")
    print("Open your browser at: http://localhost:8000")
    print("=" * 50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
