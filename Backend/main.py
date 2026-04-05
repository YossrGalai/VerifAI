import os
import shutil
import requests
import logging
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.context_service import build_context
from services.llm_service import analyze_with_llm
from services.reasoning_ai import apply_reasoning
from services.url_service import fetch_article_from_url
from services.source_detector import detect_image_origin
from services.post_service import fetch_post_data  # ← nouveau

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Trust AI — Vérificateur d'images", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(None),
    url: str = Form(None),
    article_url: str = Form(None),
    caption: str = Form(None),
):
    try:
        if not file and not url:
            raise HTTPException(status_code=400, detail="Veuillez fournir un fichier ou une URL d'image")

        image_path = None
        origin_data = {
            "origin": "Inconnu",
            "first_seen": "Inconnu",
            "reuse_count": 0,
            "best_source": None
        }

        # 🔥 Gestion URL directe Instagram/Twitter
        if url and ("twitter.com" in url or "instagram.com" in url):
            post_data = fetch_post_data(url)
            url = post_data.get("image_url") or url
            origin_data = {
                "origin": post_data.get("origin", "Inconnu"),
                "first_seen": post_data.get("first_seen", "Inconnu"),
                "reuse_count": 0,
                "best_source": {"link": url},
            }

        # Gestion fichier local
        if file:
            import uuid
            safe_filename = os.path.basename(file.filename) if file.filename else "image.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{safe_filename}")
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            image_path = file_path

        # Gestion URL normale
        elif url:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                file_path = os.path.join(UPLOAD_FOLDER, "url_image.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                image_path = file_path
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Impossible télécharger l'image: {str(e)[:50]}")

        # Article scraping
        article_data = {}
        if article_url:
            article_data = await fetch_article_from_url(article_url)
            if not image_path and article_data.get("tmp_path"):
                image_path = article_data["tmp_path"]

        # Build context
        try:
            context = build_context(
                image_path=image_path,
                image_url=url,
                article_data=article_data,
                caption=caption,
            )
            # 🔥 Si pas URL post, on détecte origine via reverse image
            if not origin_data.get("first_seen") or origin_data["first_seen"] == "Inconnu":
                origin_data = detect_image_origin(context.get("reverse_image", {}).get("results", []))
        except Exception as e:
            context = {
                "ocr": {"success": False, "text": None, "error": str(e)},
                "reverse_image": {"success": False, "results": [], "error": str(e)},
                "article": {"title": "", "text": "", "image_urls": []},
                "suspicious_signals": [],
            }

        # Cleanup temp image from article
        tmp = article_data.get("tmp_path")
        if tmp:
            try:
                os.remove(tmp)
            except Exception:
                pass

        # LLM Analysis
        llm_result = analyze_with_llm(context)

        # Reasoning
        final_decision = apply_reasoning(context, llm_result)

        # Normalize verdict
        raw_verdict = final_decision.get("final_verdict", "unc")
        VERDICT_NORMALIZE = {
            "real": "real", "mis": "mis", "unc": "unc",
            "réel": "real", "trompeur": "mis", "incertain": "unc",
            "authentique": "real", "faux": "mis",
        }
        verdict = VERDICT_NORMALIZE.get(raw_verdict.lower(), "unc")

        # Findings enrichis
        contradictions = final_decision.get("contradictions", [])
        notes = final_decision.get("reasoning_notes", [])
        findings = [f for f in contradictions + notes if f.lower() not in {"aucune contradiction détectée.", "analyse complétée"}]

        # 🔥 Ajout origin_data
        if origin_data["reuse_count"] > 0:
            findings.append(f"Image détectée sur {origin_data['reuse_count']} source(s)")
        if origin_data["first_seen"] != "Inconnu":
            findings.append(f"Première apparition : {origin_data['first_seen']}")
        findings.append(f"Source principale : {origin_data['best_source']['link'] if origin_data['best_source'] else 'N/A'}")
        findings.append(f"Origine : {origin_data['origin']}")

        if not findings:
            findings = ["Aucun élément significatif trouvé"]

        # Score fixe mais logique
        base_score = 40
        if origin_data["reuse_count"] > 2:
            base_score += 20
        if "événement fort" in " ".join(findings):
            base_score += 10
        score = min(100, base_score)

        # Label & color
        label_map = {"real": "Authentique", "mis": "Trompeur", "unc": "Incertain"}
        color_map = {"real": "#14C88C", "mis": "#FF6B6B", "unc": "#F59E0B"}
        label = label_map[verdict]
        color = color_map[verdict]

        # Axes cohérents
        axes = [
            {"name": "Cohérence temporelle",           "score": score, "color": color},
            {"name": "Cohérence géographique",         "score": score, "color": color},
            {"name": "Correspondance caption-visuel",  "score": score, "color": color},
            {"name": "Crédibilité source",             "score": score, "color": color},
        ]

        # Conclusion
        conclusion = llm_result.get("analysis", "") or "Analyse complétée"
        if len(conclusion) > 600:
            conclusion = conclusion[:600] + "…"

        ocr_text = context.get("ocr", {}).get("text", "") or context.get("ocr", {}).get("error", "")

        meta = {
            "Origin": origin_data["origin"],
            "First seen": origin_data["first_seen"],
            "Reuse count": f"{origin_data['reuse_count']} sources",
            "Best source": origin_data["best_source"]["link"] if origin_data["best_source"] else "N/A",
            "OCR": ocr_text[:100] if ocr_text else "Non disponible",
        }

        return {
            "verdict": verdict,
            "label": label,
            "score": score,
            "axes": axes,
            "findings": findings,
            "conclusion": conclusion,
            "meta": meta,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)[:50]}")


@app.post("/verify/")
async def verify_image(
    file: UploadFile = File(...),
    image_url: str = Form(None),
):
    return await analyze_image(file=file, url=image_url, caption=None)


@app.get("/")
def root():
    return {"message": "Trust AI pipeline opérationnel. POST /verify/ pour analyser une image."}