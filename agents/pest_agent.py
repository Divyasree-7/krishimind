from groq import Groq
from datetime import datetime
from config.settings import GROQ_API_KEY, GROQ_MODEL, SEASONS
from data.pest_data import get_pest_risks, get_general_pest_alert

client = Groq(api_key=GROQ_API_KEY)


def detect_season(month: str = None) -> str:
    month = month or datetime.now().strftime("%B")
    for season, months in SEASONS.items():
        if month in months:
            return season
    return "kharif"


class PestDiseaseAgent:
    def __init__(self):
        self.name = "PestDiseaseAgent"

    def run(self, query: str, context: dict = None) -> str:
        ctx = context or {}
        crop = ctx.get("crop", "wheat")
        state = ctx.get("state", "Maharashtra")
        month = ctx.get("month", datetime.now().strftime("%B"))
        season = detect_season(month)

        pest_risks = get_pest_risks(crop, season, month)
        general_alert = get_general_pest_alert(season, month)

        if pest_risks:
            pest_context = "\n".join([
                f"- {p['pest']} (Risk: {p['risk']})\n"
                f"  Symptoms: {p['symptoms']}\n"
                f"  Prevention: {p['prevention']}"
                for p in pest_risks
            ])
        else:
            pest_context = f"No specific high-risk pests for {crop} in {month}. General vigilance advised."

        prompt = f"""You are KrishiMind's Pest & Disease Risk Agent. You help Indian farmers
identify, prevent, and control pests and diseases in their crops.

Farmer context:
- Crop: {crop}
- State: {state}
- Current month: {month}
- Season: {season}

Farmer's question: {query}

Pest Risk Data for {crop} in {season} season:
{pest_context}

General Seasonal Alert:
{general_alert}

Instructions:
- List the top 1-2 pest/disease threats right now for this crop
- Describe symptoms to look for
- Give clear, actionable prevention steps
- Mention organic/natural options if available
- Use simple language; Hinglish is fine
- Keep under 250 words
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_current_risks(self, crop: str, month: str = None) -> list:
        month = month or datetime.now().strftime("%B")
        season = detect_season(month)
        return get_pest_risks(crop, season, month)
