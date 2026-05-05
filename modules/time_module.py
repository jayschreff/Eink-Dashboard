from datetime import datetime


def get_data(config):
    return {
        "id": "time",
        "title": "Time",
        "data": {
            "time": datetime.now().strftime("%I:%M %p"),
            "location": config["location"]["name"]
        }
    }