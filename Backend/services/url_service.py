import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional
import tempfile
import os


async def fetch_article_from_url(url: str) -> dict:
    """
    Scrape un article depuis une URL.
    Retourne : titre, texte complet, liste d'URLs d'images, première image téléchargée (tmp_path).
    Ne lève jamais d'exception — retourne un dict vide en cas d'échec.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    empty = {"title": "", "full_text": "", "image_urls": [], "tmp_path": None}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except Exception as e:
        empty["full_text"] = f"Scraping échoué : {str(e)}"
        return empty

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # --- Titre ---
        title = ""
        if soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # --- Texte principal ---
        body_tag = (
            soup.find("article")
            or soup.find("main")
            or soup.find(class_=lambda c: c and "article" in c.lower())
            or soup.body
        )
        paragraphs = body_tag.find_all("p") if body_tag else []
        full_text = "\n".join(
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        )

        # --- Images ---
        image_tags = soup.find_all("img")
        image_urls = []
        for img in image_tags:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src:
                absolute = urljoin(url, src)
                if not any(
                    skip in absolute.lower()
                    for skip in ["pixel", "icon", "logo", ".svg", ".gif", "tracking", "spacer"]
                ):
                    image_urls.append(absolute)

        image_urls = image_urls[:5]

        # --- Télécharge la première image valide ---
        tmp_path = await _download_first_image(image_urls)

        return {
            "title": title,
            "full_text": full_text[:3000],
            "image_urls": image_urls,
            "tmp_path": tmp_path,
        }

    except Exception as e:
        empty["full_text"] = f"Parsing échoué : {str(e)}"
        return empty


async def _download_first_image(image_urls: list) -> Optional[str]:
    """Télécharge la première image disponible. Retourne None si aucune ne fonctionne."""
    if not image_urls:
        return None

    async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
        for img_url in image_urls:
            try:
                r = await client.get(img_url)
                content_type = r.headers.get("content-type", "")
                if r.status_code == 200 and "image" in content_type:
                    suffix = ".png" if "png" in content_type else ".jpg"
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp.write(r.content)
                    tmp.close()
                    return tmp.name
            except Exception:
                continue

    return None