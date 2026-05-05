import requests
from datetime import datetime, timedelta


# ---------- CACHE ----------
_weather_cache = {
    "timestamp": None,
    "data": None
}

CACHE_DURATION = timedelta(minutes=10)  # 🔥 adjust as needed


# ---------- Weather Code Mappings ----------

def weather_code_to_icon(code):
    mapping = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️",
        56: "🌧️", 57: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        66: "🌧️", 67: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
        80: "🌦️", 81: "🌦️", 82: "🌧️",
        85: "❄️", 86: "❄️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return mapping.get(code, "☁️")


def weather_code_to_text(code):
    mapping = {
        0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Fog",
        51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
        56: "Freezing Drizzle", 57: "Freezing Drizzle",
        61: "Rain", 63: "Rain", 65: "Heavy Rain",
        66: "Freezing Rain", 67: "Freezing Rain",
        71: "Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
        80: "Rain Showers", 81: "Rain Showers", 82: "Heavy Showers",
        85: "Snow Showers", 86: "Heavy Snow Showers",
        95: "Thunderstorm", 96: "Thunderstorm", 99: "Severe Thunderstorm"
    }
    return mapping.get(code, "Unknown")


# ---------- Main Weather Module ----------

def get_data(config):
    global _weather_cache

    now = datetime.utcnow()

    # ✅ RETURN CACHED DATA IF STILL VALID
    if (
        _weather_cache["timestamp"] is not None
        and now - _weather_cache["timestamp"] < CACHE_DURATION
    ):
        return _weather_cache["data"]

    lat = config["location"]["lat"]
    lon = config["location"]["lon"]
    location_name = config["location"]["name"]
    units = config.get("units", "imperial")

    if units == "imperial":
        temp_unit = "fahrenheit"
        wind_unit = "mph"
        temp_symbol = "°F"
    else:
        temp_unit = "celsius"
        wind_unit = "kmh"
        temp_symbol = "°C"

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=apparent_temperature,relativehumidity_2m"
        f"&daily=weathercode,temperature_2m_max"
        f"&temperature_unit={temp_unit}"
        f"&windspeed_unit={wind_unit}"
        f"&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current_weather")
        if not current:
            raise ValueError("Missing current weather data")

        hourly = data.get("hourly", {})
        current_time = current.get("time")
        times = hourly.get("time", [])
        idx = times.index(current_time) if current_time in times else 0

        feels_like = hourly.get("apparent_temperature", ["--"])[idx]

        daily = data.get("daily", {})
        days = daily.get("time", [])
        temps = daily.get("temperature_2m_max", [])
        codes = daily.get("weathercode", [])

        forecast = []
        for i in range(1, 5):
            if i < len(days):
                forecast.append({
                    "day": datetime.fromisoformat(days[i]).strftime("%a"),
                    "temp": f"{temps[i]}{temp_symbol}",
                    "icon": weather_code_to_icon(codes[i])
                })

        result = {
            "id": "weather",
            "title": location_name,
            "data": {
                "temp": f"{current.get('temperature', '--')}{temp_symbol}",
                "feels_like": f"{feels_like}{temp_symbol}",
                "icon": weather_code_to_icon(current.get("weathercode", -1)),
                "status": weather_code_to_text(current.get("weathercode", -1)),
                "forecast": forecast
            }
        }

        # ✅ STORE IN CACHE
        _weather_cache = {
            "timestamp": now,
            "data": result
        }

        return result

    except Exception as e:
        print(f"[Weather Error] {e}")

        return {
            "id": "weather",
            "title": location_name,
            "data": {
                "temp": "--",
                "feels_like": "--",
                "icon": "☁️",
                "status": "Unavailable",
                "forecast": [],
                "error": str(e)
            }
        }