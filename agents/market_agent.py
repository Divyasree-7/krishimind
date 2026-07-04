from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL
from tools.market_tools import get_mandi_price, get_price_trend, get_best_selling_markets

client = Groq(api_key=GROQ_API_KEY)


class MarketPriceAgent:
    def __init__(self):
        self.name = "MarketPriceAgent"

    def run(self, query: str, context: dict = None) -> str:
        ctx = context or {}
        crop = ctx.get("crop", "wheat")
        state = ctx.get("state", "Maharashtra")

        price_data = get_mandi_price(crop, state)
        trend_data = get_price_trend(crop)
        best_markets = get_best_selling_markets(crop, state)

        if "error" in price_data:
            market_context = f"Price data error: {price_data['error']}"
        else:
            market_context = f"""
Current mandi price for {crop} in {state}: ₹{price_data['current_price_per_quintal']}/quintal
MSP (Minimum Support Price): ₹{price_data['msp_per_quintal']}/quintal
Price vs MSP: {price_data['price_vs_msp']} ({price_data['pct_above_msp']}%)
Price trend (7 days): {trend_data.get('direction', 'unknown')}
Trend recommendation: {trend_data.get('recommendation', '')}
Best markets to sell in {state}: {', '.join(best_markets)}
"""

        prompt = f"""You are KrishiMind's Market Price Agent. You help Indian farmers
get the best price for their produce and make smart selling decisions.

Farmer context:
- Crop: {crop}
- State: {state}

Farmer's question: {query}

Market Data:
{market_context}

Instructions:
- Give clear advice on whether to sell now or wait
- Mention the best markets to visit
- Compare with MSP if relevant
- Flag if price is below MSP
- Keep it under 200 words
- Simple English or Hinglish
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_price_info(self, crop: str, state: str = "Maharashtra") -> dict:
        return get_mandi_price(crop, state)
