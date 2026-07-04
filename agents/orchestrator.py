from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL
from agents.weather_agent import WeatherAgent
from agents.crop_agent import CropAdvisoryAgent
from agents.market_agent import MarketPriceAgent
from agents.pest_agent import PestDiseaseAgent

client = Groq(api_key=GROQ_API_KEY)

AGENT_ROUTING_PROMPT = """You are the orchestrator for KrishiMind, a multi-agent AI farming assistant.
Given a farmer's query, decide which agents to call.

Available agents:
- weather: Questions about rain, temperature, forecast, irrigation, weather risk
- crop: Questions about what to grow, which variety, sowing time, soil prep, fertilizer
- market: Questions about mandi price, when to sell, MSP, which market to go to
- pest: Questions about pests, insects, disease, yellowing leaves, crop damage, prevention

Respond with ONLY a comma-separated list of agent names to invoke (no explanation, no extra text).
Examples:
- "Will it rain this week?" -> weather
- "Which crop should I grow in black soil?" -> crop
- "What is onion price today?" -> market
- "My wheat leaves are turning yellow" -> pest
- "Should I sow cotton now given the weather?" -> weather,crop
- "Best crop to grow and sell at good price?" -> crop,market

Query: {query}
Agents to invoke:"""


class OrchestratorAgent:
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAdvisoryAgent()
        self.market_agent = MarketPriceAgent()
        self.pest_agent = PestDiseaseAgent()
        self.name = "OrchestratorAgent"

    def route_query(self, query: str) -> list:
        prompt = AGENT_ROUTING_PROMPT.format(query=query)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip().lower()
        agents = [a.strip() for a in raw.split(",") if a.strip() in ["weather", "crop", "market", "pest"]]
        return agents if agents else ["crop"]

    def run(self, query: str, context: dict = None) -> dict:
        ctx = context or {}
        language = ctx.get("language", "auto")
        agents_to_call = self.route_query(query)
        agent_outputs = {}

        if "weather" in agents_to_call:
            agent_outputs["weather"] = self.weather_agent.run(query, ctx.get("location"))
        if "crop" in agents_to_call:
            agent_outputs["crop"] = self.crop_agent.run(query, ctx)
        if "market" in agents_to_call:
            agent_outputs["market"] = self.market_agent.run(query, ctx)
        if "pest" in agents_to_call:
            agent_outputs["pest"] = self.pest_agent.run(query, ctx)

        if len(agent_outputs) == 1:
            final_response = list(agent_outputs.values())[0]
        else:
            final_response = self._synthesize(query, agent_outputs, language)

        if language != "auto":
            final_response = self._translate(final_response, language)

        return {
            "query": query,
            "agents_used": agents_to_call,
            "agent_outputs": agent_outputs,
            "final_response": final_response
        }

    def _synthesize(self, query: str, agent_outputs: dict, language: str = "auto") -> str:
        sections = "\n\n".join([
            f"[{name.upper()} AGENT]\n{output}"
            for name, output in agent_outputs.items()
        ])
        prompt = f"""You are KrishiMind, an AI farming assistant for Indian smallholder farmers.
Multiple specialist agents have analyzed the farmer's question.
Combine their insights into one clear, helpful, non-repetitive response.

Farmer's question: {query}

Agent insights:
{sections}

Instructions:
- Combine all insights naturally - no section headers
- Prioritize the most actionable advice
- Keep total response under 300 words
- Warm, simple tone like a helpful knowledgeable friend
- Hinglish is fine if the question has Hindi
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _translate(self, text: str, language: str) -> str:
        lang_names = {
            "hindi": "Hindi (Devanagari script)",
            "marathi": "Marathi (Devanagari script)",
            "punjabi": "Punjabi (Gurmukhi script)",
            "telugu": "Telugu script",
            "english": "simple English"
        }
        target = lang_names.get(language, language)
        prompt = f"""Translate the following farming advice into {target}.
Keep it natural, warm, and easy for a farmer to understand. Keep any rupee amounts and numbers as-is.

Text to translate:
{text}

Translated text only, no extra commentary:"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
