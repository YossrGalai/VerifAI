import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

def fetch_post_data(url: str) -> dict:
    """
    Récupère l'image, la date et l'auteur d'un post Instagram ou Twitter.
    """
    result = {
        "image_url": None,
        "first_seen": "Inconnu",
        "origin": "Inconnu",
        "best_source": {"link": url}
    }

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text

        # ---- Twitter ----
        if "twitter.com" in url:
            # Date exacte
            date_match = re.search(r'data-time="(\d+)"', html)
            if date_match:
                timestamp = int(date_match.group(1))
                result["first_seen"] = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            # Image principale
            soup = BeautifulSoup(html, "html.parser")
            img_tag = soup.find("meta", {"property": "og:image"})
            if img_tag and img_tag.get("content"):
                result["image_url"] = img_tag["content"]
            # Auteur
            author_tag = soup.find("meta", {"name": "author"})
            if author_tag and author_tag.get("content"):
                result["origin"] = author_tag["content"]

        # ---- Instagram ----
        elif "instagram.com" in url:
            soup = BeautifulSoup(html, "html.parser")
            # Image principale
            img_tag = soup.find("meta", {"property": "og:image"})
            if img_tag and img_tag.get("content"):
                result["image_url"] = img_tag["content"]
            # Date exacte
            date_tag = soup.find("meta", {"property": "og:updated_time"})
            if date_tag and date_tag.get("content"):
                dt = datetime.utcfromtimestamp(int(date_tag["content"]))
                result["first_seen"] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            # Auteur
            author_tag = soup.find("meta", {"property": "instapp:owner_user_id"})
            if author_tag and author_tag.get("content"):
                result["origin"] = author_tag["content"]

    except Exception as e:
        logger.warning(f"Impossible de récupérer le post {url}: {str(e)}")

    return result