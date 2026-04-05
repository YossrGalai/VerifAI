from datetime import datetime

def detect_image_origin(reverse_results: list) -> dict:
    """
    Analyse les résultats de recherche inversée pour trouver :
    - première apparition
    - source la plus fiable
    - nombre de réutilisations
    """

    if not reverse_results:
        return {
            "origin": "Inconnu",
            "first_seen": "Inconnu",
            "best_source": None,
            "reuse_count": 0,
            "sources": []
        }

    parsed_results = []

    for r in reverse_results:
        date_str = r.get("date", "N/A")

        try:
            # tente de parser date
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            parsed_date = None

        parsed_results.append({
            "source": r.get("source"),
            "link": r.get("link"),
            "title": r.get("title"),
            "date": parsed_date,
            "raw_date": date_str
        })

    # 🔥 1. Trier par date (ancienne → récente)
    dated_results = [r for r in parsed_results if r["date"]]

    if dated_results:
        first = sorted(dated_results, key=lambda x: x["date"])[0]
        first_seen = first["raw_date"]
        origin = first["source"]
    else:
        first_seen = "Inconnu"
        origin = parsed_results[0]["source"]

    # 🔥 2. Choisir meilleure source (heuristique simple)
    trusted_domains = ["bbc", "reuters", "nytimes", "france24"]

    best_source = None
    for r in parsed_results:
        if any(domain in (r["link"] or "") for domain in trusted_domains):
            best_source = r
            break

    if not best_source:
        best_source = parsed_results[0]

    return {
        "origin": origin,
        "first_seen": first_seen,
        "best_source": best_source,
        "reuse_count": len(parsed_results),
        "sources": parsed_results
    }