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
                "lat": 42.1292,
                "lon": -80.0851,
                "name": "Erie, PA"
            },
            "units": "imperial"
        }