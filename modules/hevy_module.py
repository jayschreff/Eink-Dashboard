import requests
from datetime import datetime


def format_time(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%I:%M %p")
    except Exception:
        return "--"


def get_data(module_config):
    api_key = module_config.get("api_key")

    if not api_key:
        return {
            "id": "hevy",
            "title": "Workout",
            "data": {
                "next_workout": "No API key",
                "time": "--"
            }
        }

    # ✅ UPDATED AUTH (Bearer instead of x-api-key)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    url = "https://api.hevyapp.com/v1/workouts"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        print("HEVY STATUS:", response.status_code)
        print("HEVY RESPONSE:", response.text)

        response.raise_for_status()
        data = response.json()

        # Handle different possible response formats
        workouts = (
            data.get("workouts")
            or data.get("data")
            or []
        )

        if not workouts:
            return {
                "id": "hevy",
                "title": "Workout",
                "data": {
                    "next_workout": "No workouts",
                    "time": "--"
                }
            }

        workout = workouts[0]

        name = workout.get("name") or workout.get("title") or "Workout"
        start_time = workout.get("start_time") or workout.get("startTime")

        return {
            "id": "hevy",
            "title": "Workout",
            "data": {
                "next_workout": name,
                "time": format_time(start_time) if start_time else "--"
            }
        }

    except requests.exceptions.HTTPError as http_err:
        print(f"[Hevy HTTP Error] {http_err}")

        return {
            "id": "hevy",
            "title": "Workout",
            "data": {
                "next_workout": f"HTTP {response.status_code}",
                "time": "--"
            }
        }

    except Exception as e:
        print(f"[Hevy Error] {e}")

        return {
            "id": "hevy",
            "title": "Workout",
            "data": {
                "next_workout": "Error",
                "time": "--"
            }
        }