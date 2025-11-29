import os
from dotenv import load_dotenv
from pathlib import Path
import requests

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")

if not WEATHER_API_KEY:
    raise ValueError("Missing WEATHER_API_KEY in .env file")

def get_current_weather(coords: dict) -> dict:
    """
    Fetch current weather for given coordinates.

    Args:
        coords (dict): Dictionary with 'lat' and 'lon' keys (strings).

    Returns:
        dict: Current weather data from Google Weather API.
    """
    if not coords or "lat" not in coords or "lon" not in coords:
        raise ValueError("Coordinates must be provided as a dict with 'lat' and 'lon'.")

    base_url = "https://weather.googleapis.com/v1/currentConditions:lookup"
    params = {
        "key": WEATHER_API_KEY,
        "location.latitude": coords["lat"],
        "location.longitude": coords["lon"],
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return {
            "status": "success",
            "weather": response.json()
        }
    except requests.HTTPError as e:
        return {
            "status": "error",
            "message": f"HTTP error: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
