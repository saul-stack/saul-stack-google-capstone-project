import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")

if not WEATHER_API_KEY:
    raise ValueError("Missing WEATHER_API_KEY in .env file")

def get_location_from_ip() -> dict:
    """Get approximate location (city, lat, lon) from public IP address."""
    try:
        resp = requests.get("https://ipinfo.io/json")
        resp.raise_for_status()
        data = resp.json()
        loc = data.get("loc", "0,0").split(",")
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "lat": loc[0],
            "lon": loc[1]
        }
    except Exception as e:
        print(f"Could not determine location from IP: {e}")
        return {"city": None, "lat": "0", "lon": "0"}


def get_coords_for_place(place: str) -> dict:
    """
    Try to geocode any given place string (city, neighborhood, landmark).
    Raises ValueError if no valid location is found.
    """
    
    if not GEOCODING_API_KEY:
        raise ValueError("Missing GEOCODING_API_KEY in .env file")
    
    if not place:
        raise ValueError("No place name provided")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place, "key": GEOCODING_API_KEY}

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if data["status"] != "OK" or not data["results"]:
        raise ValueError(f"Could not find coordinates for place: {place}")

    location = data["results"][0]["geometry"]["location"]
    formatted_name = data["results"][0]["formatted_address"]
    return {"lat": location["lat"], "lon": location["lng"], "name": formatted_name}

