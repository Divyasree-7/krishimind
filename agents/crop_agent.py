from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL
from data.crop_knowledge import get_crop_info, recommend_crops_for_context

client = Groq(api_key=GROQ_API_KEY)


class CropAdvisoryAgent:
    def __init__(self):
        self.name = "CropAdvisoryAgent"

    def run(self, query: str, context: dict = None) -> str:
        ctx = context or {}
        soil_type = ctx.get("soil_type", "loamy")
        season = ctx.get("season", "kharif")
        state = ctx.get("state", "Maharashtra")
        crop = ctx.get("crop", None)

        if crop:
            crop_data = get_crop_info(crop)
            kb_context = f"Crop details for {crop}:\n{crop_data}" if crop_data else f"No specific data for {crop}."
        else:
            suggested = recommend_crops_for_context(soil_type, season, state)
            kb_context = f"Suitable crops for {soil_type} soil in {season} season in {state}: {', '.join(suggested)}"

        prompt = f"""You are KrishiMind's Crop Advisory Agent, trained on ICAR guidelines and
Indian agricultural best practices.

Farmer context:
- State: {state}
- Season: {season}
- Soil type: {soil_type}
- Specific crop asked about: {crop or 'Not specified'}

Farmer's question: {query}

Knowledge Base:
{kb_context}

Instructions:
- Give practical, specific crop advice
- Include sowing time, soil prep tips, or variety suggestions where relevant
- If recommending multiple crops, explain the top 2-3 with brief reasoning
- Use simple language; Hinglish is fine if question has Hindi
- Keep response under 250 words
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_crop_recommendations(self, soil_type: str, season: str, state: str) -> list:
        return recommend_crops_for_context(soil_type, season, state)
