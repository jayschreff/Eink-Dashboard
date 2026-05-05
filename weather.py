import requests
from datetime import datetime


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

        current = data.get("current_weather")
        if not current:
            raise ValueError("Missing current_weather data")

        hourly = data.get("hourly", {})

        # ✅ FIXED: match correct hour
        current_time = current.get("time")
        hourly_times = hourly.get("time", [])
        index = hourly_times.index(current_time) if current_time in hourly_times else 0

        feels_like = hourly.get("apparent_temperature", ["--"])[index]
        humidity = hourly.get("relativehumidity_2m", ["--"])[index]

        daily = data.get("daily", {})
        forecast = []

        days = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        codes = daily.get("weathercode", [])

        for i in range(1, 5):
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