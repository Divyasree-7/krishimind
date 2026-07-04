from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL, DEFAULT_LOCATION
from tools.weather_tools import get_weather_forecast, compute_rainfall_risk, parse_weather_summary

client = Groq(api_key=GROQ_API_KEY)


class WeatherAgent:
    def __init__(self):
        self.name = "WeatherAgent"

    def run(self, query: str, location: dict = None) -> str:
        loc = location or DEFAULT_LOCATION
        lat = loc.get("latitude", DEFAULT_LOCATION["latitude"])
        lon = loc.get("longitude", DEFAULT_LOCATION["longitude"])
        loc_name = loc.get("name", DEFAULT_LOCATION["name"])

        forecast_data = get_weather_forecast(lat, lon)
        weather_summary = parse_weather_summary(forecast_data)
        rainfall_risk = compute_rainfall_risk(forecast_data)

        prompt = f"""You are KrishiMind's Weather & Climate Agent. Your job is to give simple,
actionable weather advice to a smallholder farmer in India.

Location: {loc_name}
Farmer's question: {query}

Weather Data:
{weather_summary}

Rainfall Risk Assessment:
- Risk Level: {rainfall_risk['risk_level']}
- Expected Rain (7 days): {rainfall_risk['total_expected_rain_mm']} mm
- Rain Probability: {rainfall_risk['avg_rain_probability_pct']}%
- Advisory: {rainfall_risk['message']}

Instructions:
- Answer in simple English (or Hinglish if the question has Hindi words)
- Give 2-3 specific farming actions based on the weather
- Keep it under 200 words
- Be warm and direct, like a knowledgeable friend
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_raw_forecast(self, location: dict = None) -> dict:
        loc = location or DEFAULT_LOCATION
        return get_weather_forecast(loc["latitude"], loc["longitude"])
