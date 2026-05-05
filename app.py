from flask import Flask, render_template

from config import load_config
from weather import get_weather
from utils import get_time, weather_code_to_text, weather_code_to_icon

app = Flask(__name__)


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
        "forecast": weather["forecast"],
        "location": location_name,
        "error": weather["error"]
    }

    return render_template(
        "index.html",
        data=data,
        weather_code_to_icon=weather_code_to_icon
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)