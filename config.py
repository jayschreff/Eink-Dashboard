import json
import os


def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "config.json")

        with open(path) as f:
            return json.load(f)

    except FileNotFoundError:
        print("Missing config.json — using defaults")
        return {
            "location": {
                "lat": 42.1145,
                "lon": -80.0762,
                "name": "Erie, PA"
            },
            "units": "imperial",
            "modules": [
                {"name": "time", "enabled": True},
                {"name": "weather", "enabled": True},
                {"name": "hevy", "enabled": False}
            ]
        }