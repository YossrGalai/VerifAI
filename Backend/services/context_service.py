from services.ocr import perform_ocr
from services.reverse_image import reverse_image_search


def build_context(
    image_path: str,
    image_url: str = None,
    article_data: dict = None,
    caption: str = None,
) -> dict:
    """
    Construit le contexte complet pour l'analyse LLM.
    """
    # OCR
    ocr_result = perform_ocr(image_path) if image_path else {
        "success": False, "text": None, "error": "Aucun fichier image fourni."
    }

    # Reverse image search (nécessite une URL publique)
    if image_url and image_url.startswith("http"):
        reverse_result = reverse_image_search(image_url)
    else:
        reverse_result = {
            "success": False,
            "results": [],
            "error": "Aucune URL publique fournie — recherche inversée ignorée."
        }

    # Données article optionnelles
    article_title      = ""
    article_text       = ""
    article_image_urls = []
    if article_data:
        article_title      = article_data.get("title", "")
        article_text       = article_data.get("full_text", "")
        article_image_urls = article_data.get("image_urls", [])

    context = {
        "caption": caption or "",          # ← transmis au LLM
        "ocr": {
            "success": ocr_result["success"],
            "text":    ocr_result.get("text"),
            "error":   ocr_result.get("error"),
        },
        "reverse_image": {
            "success": reverse_result["success"],
            "results": reverse_result.get("results", []),
            "error":   reverse_result.get("error"),
        },
        "article": {
            "title":      article_title,
            "text":       article_text,
            "image_urls": article_image_urls,
        },
        "suspicious_signals": _detect_suspicious_signals(
            ocr_result, reverse_result, article_text
        ),
    }

    return context


def _detect_suspicious_signals(
    ocr_result: dict,
    reverse_result: dict,
    article_text: str = "",
) -> list:
    signals = []
    ocr_text = ocr_result.get("text") or ""
    sources  = reverse_result.get("results", [])

    if ocr_result["success"] and not ocr_text:
        signals.append("Aucun texte détecté malgré une image soumise.")

    dates_found = [s["date"] for s in sources if s.get("date") and s["date"] != "N/A"]
    if dates_found:
        signals.append(
            f"Image trouvée sur {len(sources)} source(s). Dates : {', '.join(dates_found)}"
        )

    if reverse_result["success"] and not sources:
        signals.append("Aucune source externe trouvée — image potentiellement originale ou générée.")

    if article_text and len(article_text) < 100:
        signals.append("Contenu de l'article très court — source potentiellement peu fiable.")

    return signals