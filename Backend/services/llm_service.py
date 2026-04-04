import openai
async def analyze_with_llm(caption, image_desc, context):

    # simple fake logic (pour tester)
    if "now" in caption.lower():
        verdict = "Misleading"
        confidence = 90
        explanation = "Caption claims real-time event but image is from archived context"
    else:
        verdict = "Uncertain"
        confidence = 60
        explanation = "Not enough temporal information"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": explanation
    }