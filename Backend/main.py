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
        # Validate inputs
        if not file and not url:
            logger.warning("No file or URL provided")
            raise HTTPException(status_code=400, detail="Veuillez fournir un fichier ou une URL d'image")

        image_path = None

        try:
            if file:
                safe_filename = os.path.basename(file.filename) if file.filename else "image.jpg"
                file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                image_path = file_path
                logger.info(f"File saved: {file_path}")

            elif url:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    file_path = os.path.join(UPLOAD_FOLDER, "url_image.jpg")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    image_path = file_path
                    logger.info(f"Image downloaded from URL: {url}")
                except Exception as e:
                    logger.error(f"URL download failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Impossible télécharger l'image: {str(e)[:50]}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File handling error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Erreur traitement fichier: {str(e)[:50]}")

        # Article scraping
        article_data = {}
        if article_url:
            article_data = await fetch_article_from_url(article_url)
            logger.info(f"Article scrapé : {article_data.get('title', 'sans titre')}")
            if not image_path and article_data.get("tmp_path"):
                image_path = article_data["tmp_path"]

        # Build context
        try:
            context = build_context(
                image_path=image_path,
                image_url=url,
                article_data=article_data,
                caption=caption,          # ← caption transmis au LLM
            )
            logger.info("Context built successfully")
        except Exception as e:
            logger.error(f"Context building error: {str(e)}")
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
        try:
            llm_result = analyze_with_llm(context)
            logger.info(f"LLM result: {llm_result}")          # ← log complet pour debug
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            llm_result = {"success": False, "analysis": "Analyse LLM échouée", "error": str(e)}

        # Reasoning
        try:
            final_decision = apply_reasoning(context, llm_result)
            logger.info(f"Final decision: {final_decision}")  # ← log complet pour debug
        except Exception as e:
            logger.error(f"Reasoning error: {str(e)}")
            final_decision = {
                "final_verdict": "unc",
                "confidence": 0,
                "contradictions": [],
                "reasoning_notes": ["Erreur dans le raisonnement"],
            }

        # ── FIX 1 : mapping étendu qui couvre les deux formats ──────────────
        raw_verdict = final_decision.get("final_verdict", "unc")

        VERDICT_NORMALIZE = {
            # format court (nouveau)
            "real": "real",
            "mis":  "mis",
            "unc":  "unc",
            # format long français (ancien reasoning_ai)
            "réel":      "real",
            "trompeur":  "mis",
            "incertain": "unc",
            # variantes possibles
            "authentique": "real",
            "faux":        "mis",
        }
        verdict = VERDICT_NORMALIZE.get(raw_verdict.lower(), "unc")

        score = min(100, max(0, int(final_decision.get("confidence", 0))))

        label_map = {"real": "Authentique", "mis": "Trompeur", "unc": "Incertain"}
        color_map = {"real": "#14C88C",     "mis": "#FF6B6B",  "unc": "#F59E0B"}

        label = label_map[verdict]
        color = color_map[verdict]

        axes = [
            {"name": "Cohérence temporelle",           "score": score, "color": color},
            {"name": "Cohérence géographique",         "score": score, "color": color},
            {"name": "Correspondance caption-visuel",  "score": score, "color": color},
            {"name": "Crédibilité source",             "score": score, "color": color},
        ]

        # ── FIX 2 : findings = contradictions + notes (plus riche) ──────────
        contradictions = final_decision.get("contradictions", [])
        notes          = final_decision.get("reasoning_notes", [])

        # Filtre les messages génériques inutiles
        SKIP = {"aucune contradiction détectée.", "analyse complétée"}
        findings = [f for f in contradictions + notes if f.lower() not in SKIP]
        if not findings:
            findings = ["Aucun élément significatif trouvé"]

        conclusion = final_decision.get("llm_analysis", "") or " ".join(notes) or "Analyse complétée"
        # Tronquer si trop long
        if len(conclusion) > 600:
            conclusion = conclusion[:600] + "…"

        ocr_text     = context.get("ocr", {}).get("text", "") or context.get("ocr", {}).get("error", "")
        reverse_count = len(context.get("reverse_image", {}).get("results", []))

        meta = {
            "Origin":      "À déterminer",
            "Reuse count": f"{reverse_count} sources" if reverse_count > 0 else "Aucune réutilisation",
            "First seen":  "À déterminer",
            "Language":    "À déterminer",
            "OCR":         ocr_text[:100] if ocr_text else "Non disponible",
            "Metadata":    f"Sources: {reverse_count}",
        }

        return {
            "verdict":    verdict,
            "label":      label,
            "score":      score,
            "axes":       axes,
            "findings":   findings,
            "conclusion": conclusion,
            "meta":       meta,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /analyze: {str(e)}")
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