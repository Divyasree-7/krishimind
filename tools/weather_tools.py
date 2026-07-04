import requests
from config.settings import OPEN_METEO_BASE_URL


def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> dict:
    """Fetch weather forecast from Open-Meteo API (free, no key needed)."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max",
            "weathercode"
        ],
        "current_weather": True,
        "timezone": "Asia/Kolkata",
        "forecast_days": days
    }
    try:
        response = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def compute_rainfall_risk(forecast_data: dict) -> dict:
    """Compute rainfall risk score from forecast data."""
    if "error" in forecast_data:
        return {"risk_level": "unknown", "score": 0, "message": "Could not fetch weather data."}

    daily = forecast_data.get("daily", {})
    precipitation = daily.get("precipitation_sum", [])
    precip_prob = daily.get("precipitation_probability_max", [])

    total_rain = sum(precipitation) if precipitation else 0
    avg_prob = sum(precip_prob) / len(precip_prob) if precip_prob else 0

    if total_rain > 100 or avg_prob > 80:
        risk_level = "HIGH"
        score = 8
        message = "Heavy rainfall expected. Avoid sowing. Ensure proper drainage."
    elif total_rain > 40 or avg_prob > 50:
        risk_level = "MEDIUM"
        score = 5
        message = "Moderate rainfall likely. Plan irrigation carefully."
    else:
        risk_level = "LOW"
        score = 2
        message = "Low rainfall risk. Good conditions for most field activities."

    return {
        "risk_level": risk_level,
        "score": score,
        "total_expected_rain_mm": round(total_rain, 1),
        "avg_rain_probability_pct": round(avg_prob, 1),
        "message": message
    }


def parse_weather_summary(forecast_data: dict) -> str:
    """Convert raw forecast data into a readable summary string."""
    if "error" in forecast_data:
        return f"Weather data unavailable: {forecast_data['error']}"

    current = forecast_data.get("current_weather", {})
    daily = forecast_data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_sum", [])

    summary_lines = [
        f"Current temperature: {current.get('temperature', 'N/A')}°C",
        f"Wind speed: {current.get('windspeed', 'N/A')} km/h",
        "",
        "7-Day Forecast:"
    ]
    for i in range(min(7, len(dates))):
        line = (
            f"  {dates[i]}: Max {max_temps[i]}°C / Min {min_temps[i]}°C"
            f", Rain: {rain[i]} mm"
        )
        summary_lines.append(line)

    return "\n".join(summary_lines)
