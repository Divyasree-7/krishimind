# 🌾 KrishiMind
## Agentic AI for Smallholder Farmer Resilience

**Kaggle 5-Day Gen AI Intensive — Capstone Project | Stream: Agents for Good**

A multi-agent AI system that acts as an intelligent farming companion for Indian smallholder farmers — combining real weather data, crop knowledge, market intelligence, and pest risk assessment into a unified conversational assistant.

---

## Project Structure

```
krishimind/
├── agents/
│   ├── weather_agent.py      # Weather & Climate Agent
│   ├── crop_agent.py         # Crop Advisory Agent
│   ├── market_agent.py       # Market Price Agent
│   ├── pest_agent.py         # Pest & Disease Agent
│   └── orchestrator.py       # Orchestrator (routes + synthesizes)
├── tools/
│   ├── weather_tools.py      # Open-Meteo API integration
│   └── market_tools.py       # Mandi price tools
├── data/
│   ├── crop_knowledge.py     # ICAR-backed crop knowledge base
│   └── pest_data.py          # Seasonal pest & disease database
├── ui/
│   └── app.py                # Gradio chat interface
├── config/
│   └── settings.py           # Configuration and constants
├── notebooks/
│   └── KrishiMind_Capstone.ipynb
├── main.py                   # Entry point
├── test_agents.py            # Quick agent test
├── requirements.txt
└── .env.example
```

---

## Setup & Run (VS Code)

### Step 1 — Clone / open the folder in VS Code
```bash
cd krishimind
code .
```

### Step 2 — Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up your API key
```bash
cp .env.example .env
```
Then open `.env` and replace `your_gemini_api_key_here` with your actual [Google AI Studio key](https://aistudio.google.com/app/apikey).

### Step 5 — Test all agents
```bash
python test_agents.py
```
You should see responses from all 5 agents. If you get errors, check your API key.

### Step 6 — Launch the chat UI
```bash
python main.py
```
Then open your browser at: **http://localhost:7860**

---

## Using on Kaggle

1. Upload the entire `krishimind/` folder to Kaggle
2. Open `notebooks/KrishiMind_Capstone.ipynb`
3. Add your Gemini API key to Kaggle Secrets as `GOOGLE_API_KEY`
4. Run all cells — the last cell launches the Gradio UI with a public link

---

## Agents

| Agent | What it does | Data Source |
|---|---|---|
| Weather & Climate | 7-day forecast, rainfall risk, farming alerts | Open-Meteo (free) |
| Crop Advisory | Crop recommendations by soil, season, region | ICAR knowledge base + Gemini |
| Market Price | Mandi prices, MSP comparison, sell timing | Agmarknet (mock → replace with live) |
| Pest & Disease | Outbreak alerts, symptoms, prevention | Seasonal heuristics + Gemini |
| Orchestrator | Routes queries, synthesizes all agent outputs | Gemini 1.5 Flash |

---

## Replacing Mock Data with Live APIs

The `tools/market_tools.py` currently uses mock mandi data. To connect real data:

1. Register at [Agmarknet](https://agmarknet.gov.in)
2. Replace the `get_mandi_price()` function with a real API call
3. Add your API key to `.env`

---

## Tech Stack

- **Framework:** Google ADK + `google-generativeai`
- **LLM:** Gemini 1.5 Flash
- **Weather API:** Open-Meteo (free, no key needed)
- **UI:** Gradio
- **Language:** Python 3.10+
