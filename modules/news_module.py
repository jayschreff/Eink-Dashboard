import requests


def get_data(module_config):
    api_key = module_config.get("api_key")

    if not api_key:
        return {
            "id": "news",
            "title": "News",
            "data": {
                "headlines": ["No API key"]
            }
        }

    url = (
        "https://newsapi.org/v2/top-headlines"
        "?country=us&pageSize=5"
    )

    headers = {
        "Authorization": api_key
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        headlines = [a["title"] for a in articles if a.get("title")]

        return {
            "id": "news",
            "title": "Top News",
            "data": {
                "headlines": headlines[:5]
            }
        }

    except Exception as e:
        print(f"[News Error] {e}")

        return {
            "id": "news",
            "title": "Top News",
            "data": {
                "headlines": ["Error loading news"]
            }
        }