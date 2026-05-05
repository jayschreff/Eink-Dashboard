from datetime import datetime


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