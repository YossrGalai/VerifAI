import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

try:
    from groq import Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
    else:
        logger.warning("GROQ_API_KEY not found in environment")
        client = None
except ImportError:
    logger.warning("Groq library not installed")
    client = None
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None


def analyze_with_llm(context: dict) -> dict:
    """
    Envoie le contexte structuré à Groq (LLaMA3) et retourne son analyse.
    """
    fallback = {
        "success": False,
        "analysis": "Analyse LLM non disponible",
        "error": "Service LLM indisponible"
    }

    if not client:
        return fallback
    if not context:
        return fallback

    try:
        ocr_data      = context.get("ocr", {})
        ocr_text      = ocr_data.get("text") or "Aucun texte extrait."

        reverse_data    = context.get("reverse_image", {})
        reverse_results = reverse_data.get("results") or []
        reverse_success = reverse_data.get("success", False)

        suspicious_signals = context.get("suspicious_signals") or []

        article_data  = context.get("article", {})
        article_title = article_data.get("title", "")
        article_text  = article_data.get("text", "")

        caption = context.get("caption", "")

    except Exception as e:
        logger.error(f"Error extracting context data: {e}")
        return fallback

    try:
        # Résumé reverse search
        if reverse_results:
            reverse_str = "\n".join(
                f"  - [{r.get('source','?')}] {r.get('title','?')} ({r.get('date','?')}) — {r.get('link','')}"
                for r in reverse_results
            )
        elif reverse_success:
            reverse_str = "Recherche inversée effectuée : aucune occurrence trouvée (image potentiellement originale ou très récente)."
        else:
            reverse_str = "Recherche inversée non disponible ou échouée."

        signals_str = "\n".join(f"  - {s}" for s in suspicious_signals) if suspicious_signals else "  Aucun signal suspect automatique détecté."

        # Section article optionnelle
        article_section = ""
        if article_title or article_text:
            article_section = f"""
5. CONTENU DE L'ARTICLE SOURCE :
   Titre : {article_title or 'Non disponible'}
   Texte : {article_text[:800] if article_text else 'Non disponible'}
"""

        prompt = f"""Tu es un expert en fact-checking et vérification de contenu visuel.

Voici toutes les données disponibles sur le contenu soumis :

1. DESCRIPTION / CAPTION FOURNIE PAR L'UTILISATEUR :
   « {caption or 'Aucune description fournie.'} »

2. TEXTE EXTRAIT DE L'IMAGE (OCR) :
   {ocr_text}

3. RÉSULTATS DE RECHERCHE INVERSÉE :
{reverse_str}

4. SIGNAUX SUSPECTS DÉTECTÉS AUTOMATIQUEMENT :
{signals_str}
{article_section}
---

INSTRUCTIONS :
Tu dois analyser la cohérence entre la description fournie et le contenu réel de l'image.

- Si la description contient des affirmations vérifiables (date, lieu, événement, personne), évalue leur plausibilité.
- Si la recherche inversée montre des réutilisations dans d'autres contextes, c'est un signal fort de tromperie.
- Si aucune source externe n'est trouvée, base-toi sur la logique interne de la description.
- Donne un score de confiance RÉALISTE : pas 0 sauf si vraiment aucune donnée, pas 100 sauf si tout est confirmé.

EXEMPLES DE RAISONNEMENT :
- Description vague + image générique + pas de source → Incertain, score 40-60
- Description avec date/lieu précis + image ne contenant aucun indice contradictoire → Réel, score 65-80
- Description avec affirmation forte + image réutilisée dans d'autres contextes → Trompeur, score 70-90
- Description clairement cohérente avec une image connue et bénigne → Réel, score 75-85

Réponds STRICTEMENT dans ce format (respecte les labels exacts) :

Verdict: (Réel / Trompeur / Incertain)
Score de confiance: (0-100)
Explication:
- Point 1
- Point 2
- Point 3
Conclusion finale:
(1-2 phrases maximum, claire et directe)
"""

    except Exception as e:
        logger.error(f"Error building prompt: {e}")
        return fallback

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        if response and hasattr(response, "choices") and response.choices:
            llm_text = response.choices[0].message.content
            if llm_text:
                logger.info(f"LLM raw response:\n{llm_text}")
                return {"success": True, "analysis": llm_text, "error": None}

        return fallback

    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return {
            "success": False,
            "analysis": "Analyse LLM échouée",
            "error": "Service LLM temporarily unavailable"
        }