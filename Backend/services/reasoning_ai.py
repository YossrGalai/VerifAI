import re


def apply_reasoning(context: dict, llm_result: dict) -> dict:
    """
    Couche de raisonnement logique qui enrichit l'analyse du LLM.
    Détecte les contradictions et produit une décision finale fiable.
    Les verdicts retournés sont toujours : "real" | "mis" | "unc"
    """
    decision = {
        "final_verdict":  "unc",
        "confidence":     0,
        "contradictions": [],
        "reasoning_notes": [],
        "llm_analysis":   llm_result.get("analysis"),
    }

    if not llm_result.get("success"):
        decision["reasoning_notes"].append(f"LLM indisponible : {llm_result.get('error')}")
        return decision

    analysis_text = llm_result["analysis"].lower()

    # ── Extraction du verdict LLM ────────────────────────────────────────────
    # Cherche d'abord la ligne "Verdict: ..." pour être précis
    verdict_match = re.search(r"verdict\s*:\s*(\w+)", analysis_text)
    if verdict_match:
        raw = verdict_match.group(1).lower()
        if raw in ("trompeur", "misleading", "faux", "fake"):
            llm_verdict = "mis"
        elif raw in ("réel", "reel", "real", "authentique", "authentic", "vrai"):
            llm_verdict = "real"
        else:
            llm_verdict = "unc"
    else:
        # Fallback : recherche dans tout le texte
        if any(w in analysis_text for w in ["trompeur", "misleading", "faux", "fake"]):
            llm_verdict = "mis"
        elif any(w in analysis_text for w in ["réel", "reel", "real", "authentique", "vrai"]):
            llm_verdict = "real"
        else:
            llm_verdict = "unc"

    # ── Extraction du score de confiance ────────────────────────────────────
    score_match = re.search(r"score de confiance\s*:\s*(\d+)", analysis_text)
    if not score_match:
        score_match = re.search(r"confiance\s*:\s*(\d+)", analysis_text)
    if not score_match:
        score_match = re.search(r"confidence\s*:\s*(\d+)", analysis_text)
    llm_confidence = int(score_match.group(1)) if score_match else 50

    # ── Règles de raisonnement additionnelles ───────────────────────────────
    ocr_text       = (context.get("ocr", {}).get("text") or "").lower()
    reverse_sources = context.get("reverse_image", {}).get("results", [])
    suspicious_signals = context.get("suspicious_signals", [])

    # Règle 1 : Contradiction temporelle
    years_in_text = re.findall(r'\b(19|20)\d{2}\b', ocr_text)
    years_in_sources = []
    for s in reverse_sources:
        found = re.findall(r'\b(19|20)\d{2}\b', s.get("date", "") + " " + s.get("title", ""))
        years_in_sources.extend(found)

    if years_in_text and years_in_sources:
        if set(years_in_text) != set(years_in_sources):
            decision["contradictions"].append(
                f"Contradiction temporelle : OCR mentionne {years_in_text}, "
                f"sources externes mentionnent {list(set(years_in_sources))}."
            )
            llm_confidence = max(0, llm_confidence - 20)
            llm_verdict = "mis"

    # Règle 2 : Signaux suspects → baisser la confiance
    if len(suspicious_signals) >= 2:
        llm_confidence = max(0, llm_confidence - 15)
        decision["reasoning_notes"].append("Plusieurs signaux suspects détectés — confiance réduite.")

    # Règle 3 : Aucune source trouvée pour une image avec texte → incertain
    if not reverse_sources and ocr_text:
        decision["reasoning_notes"].append(
            "Image avec texte mais sans source externe — vérification limitée."
        )
        if llm_verdict == "real":
            llm_verdict = "unc"

    # ── Décision finale ─────────────────────────────────────────────────────
    decision["final_verdict"] = llm_verdict          # "real" | "mis" | "unc"
    decision["confidence"]    = llm_confidence
    if not decision["contradictions"]:
        decision["contradictions"] = ["Aucune contradiction détectée."]

    return decision