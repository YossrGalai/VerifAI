import os
import requests
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def reverse_image_search(image_url: str) -> dict:
    """
    Recherche inversée via SerpAPI (Google Lens).
    Nécessite une URL publique (pas un chemin local).
    Retourne un dict structuré avec les résultats ou une erreur.
    """
    if not SERPAPI_KEY:
        return {"success": False, "results": [], "error": "Clé SERPAPI_KEY manquante dans .env"}

    if not image_url.startswith("http://") and not image_url.startswith("https://"):
        return {
            "success": True,
            "results": [],
            "error": "SerpAPI nécessite une URL publique. Pas de résultat trouvé."
        }

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY,
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"success": False, "results": [], "error": f"SerpAPI : {data['error']}"}

        matches = data.get("visual_matches", [])
        if not matches:
            return {"success": True, "results": [], "error": "Aucun résultat trouvé."}

        results = [
            {
                "title": m.get("title", "N/A"),
                "link": m.get("link", "N/A"),
                "source": m.get("source", "N/A"),
                "date": m.get("date", "N/A"),
                "thumbnail": m.get("thumbnail", "N/A"),
            }
            for m in matches[:4]
        ]

        return {"success": True, "results": results, "error": None}

    except requests.exceptions.Timeout:
        return {"success": False, "results": [], "error": "Timeout : SerpAPI n'a pas répondu."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "results": [], "error": f"Erreur HTTP : {str(e)}"}
    except Exception as e:
        return {"success": False, "results": [], "error": f"Erreur inattendue : {str(e)}"}