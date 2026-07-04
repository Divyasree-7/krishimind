import os
from dotenv import load_dotenv

load_dotenv()

# PASTE YOUR GROQ API KEY BELOW (get free key at https://console.groq.com/keys)
# It should start with "gsk_"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") or "PASTE_YOUR_API_KEY_HERE"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Optional: free key from https://data.gov.in/ for live mandi prices
# If left as-is, the app automatically uses realistic sample data instead
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "") or "PASTE_YOUR_DATA_GOV_KEY_HERE"

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

AGMARKNET_URL = "https://agmarknet.gov.in"

DEFAULT_LOCATION = {
    "name": "Pune, Maharashtra",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "state": "Maharashtra",
    "district": "Pune"
}

SUPPORTED_CROPS = [
    "wheat", "rice", "cotton", "soybean", "sugarcane",
    "maize", "groundnut", "onion", "tomato", "potato",
    "bajra", "jowar", "tur dal", "chana", "mustard"
]

SEASONS = {
    "kharif": ["June", "July", "August", "September", "October"],
    "rabi": ["November", "December", "January", "February", "March"],
    "zaid": ["March", "April", "May", "June"]
}
