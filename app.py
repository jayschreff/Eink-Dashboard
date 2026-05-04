import json
import requests
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


# ---------- Config ----------
def load_config():
    with open("config.json") as f:
        return json.load(f)


# ---------- Fallback ----------
def fallback_weather(message):
    print(f"[Weather Error] {message}")

    return {
        "temp": "--",
        "feels_like": "--",
        "humidity": "--",
        "windspeed": "--",
        "code": -1,
        "forecast": [],
        "error": message
    }


# ---------- Weather ----------
def get_weather(lat, lon, units):
    if units == "imperial":
        temp_unit = "fahrenheit"
        wind_unit = "mph"
        temp_symbol = "°F"
        wind_label = "mph"
    else:
        temp_unit = "celsius"
        wind_unit = "kmh"
        temp_symbol = "°C"
        wind_label = "km/h"

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=relativehumidity_2m,apparent_temperature"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
        f"&temperature_unit={temp_unit}"
        f"&windspeed_unit={wind_unit}"
        f"&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # ---------- Current ----------
        current = data.get("current_weather")
        if not current:
            raise ValueError("Missing current_weather data")

        hourly = data.get("hourly", {})
        feels_like = hourly.get("apparent_temperature", ["--"])[0]
        humidity = hourly.get("relativehumidity_2m", ["--"])[0]

        # ---------- Forecast ----------
        daily = data.get("daily", {})

        forecast = []
        days = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        codes = daily.get("weathercode", [])

        for i in range(1, 5):  # next 4 days
            if i < len(days):
                day_name = datetime.fromisoformat(days[i]).strftime("%a")

                forecast.append({
                    "day": day_name,
                    "temp": f"{temps_max[i]}{temp_symbol}",
                    "code": codes[i]
                })

        return {
            "temp": f"{current.get('temperature', 'N/A')}{temp_symbol}",
            "feels_like": f"{feels_like}{temp_symbol}",
            "humidity": f"{humidity}%",
            "windspeed": f"{current.get('windspeed', 'N/A')} {wind_label}",
            "code": current.get("weathercode", -1),
            "forecast": forecast,
            "error": None
        }

    except Exception as e:
        return fallback_weather(str(e))


# ---------- Helpers ----------
def get_time():
    return datetime.now().strftime("%I:%M %p")


def weather_code_to_text(code):
    mapping = {
        0: "Clear",
        1: "Mostly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Light Drizzle",
        61: "Rain",
        63: "Rain",
        65: "Heavy Rain",
        71: "Snow",
        73: "Snow",
        75: "Heavy Snow",
        80: "Rain Showers",
        95: "Thunderstorm"
    }
    return mapping.get(code, "Unknown")


def weather_code_to_icon(code):
    mapping = {
        0: "☀️",
        1: "🌤️",
        2: "⛅",
        3: "☁️",
        45: "🌫️",
        48: "🌫️",
        51: "🌦️",
        61: "🌧️",
        63: "🌧️",
        65: "🌧️",
        71: "❄️",
        73: "❄️",
        75: "❄️",
        80: "🌦️",
        95: "⛈️"
    }
    return mapping.get(code, "❓")


# ---------- Routes ----------
@app.route("/")
def home():
    config = load_config()

    lat = config["location"]["lat"]
    lon = config["location"]["lon"]
    location_name = config["location"]["name"]
    units = config.get("units", "imperial")

    weather = get_weather(lat, lon, units)

    data = {
        "temp": weather["temp"],
        "feels_like": weather["feels_like"],
        "humidity": weather["humidity"],
        "windspeed": weather["windspeed"],
        "time": get_time(),
        "status": weather_code_to_text(weather["code"]),
        "icon": weather_code_to_icon(weather["code"]),
        "forecast": weather["forecast"],  # ✅ ADDED
        "location": location_name,
        "error": weather["error"]
    }

    return render_template(
        "index.html",
        data=data,
        weather_code_to_icon=weather_code_to_icon
    )


# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)