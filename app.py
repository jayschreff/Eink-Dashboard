from flask import Flask, render_template

from config import load_config

# Module imports
from modules.time_module import get_data as get_time_module
from modules.weather_module import get_data as get_weather_module
from modules.news_module import get_data as get_news_module
from modules.bambu_module import get_data as get_bambu_module
# from modules.hevy_module import get_data as get_hevy_module  # optional (currently unused)

app = Flask(__name__)


@app.route("/")
def home():
    config = load_config()

    modules_output = []

    for module in config.get("modules", []):
        if not module.get("enabled", True):
            continue

        name = module.get("name")

        if name == "time":
            modules_output.append(get_time_module(config))

        elif name == "weather":
            modules_output.append(get_weather_module(config))

        elif name == "news":
            modules_output.append(get_news_module(module))

        elif name == "bambu":
            modules_output.append(get_bambu_module(module))

        # elif name == "hevy":
        #     modules_output.append(get_hevy_module(module))

    return render_template("index.html", modules=modules_output)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)