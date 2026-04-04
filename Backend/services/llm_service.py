import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def safe_extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")
    return json.loads(match.group())


def normalize_response(data: dict) -> dict:
    # 🔥 FORCE axes TO ALWAYS BE A LIST
    if not isinstance(data.get("axes"), list):
        data["axes"] = []

    # safety for each axis item
    cleaned_axes = []
    for a in data["axes"]:
        if isinstance(a, dict):
            cleaned_axes.append({
                "name": a.get("name", "unknown"),
                "score": a.get("score", 0),
                "color": a.get("color", "#14C88C"),
            })

    data["axes"] = cleaned_axes
    return data


async def get_llm_verdict(caption: str, image_description: str, image_context: str) -> dict:

    api_key = os.getenv("GROQ_KEY")

    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY")

    client = Groq(api_key=api_key)

    prompt = f"""
Return ONLY valid JSON.

Caption: {caption}
Image: {image_description}
Context: {image_context}

Return format:
{{
  "verdict": "mis" | "real" | "unc",
  "label": "Misleading" | "Authentic" | "Uncertain",
  "score": 0-100,
  "axes": [
    {{"name": "Temporal consistency", "score": 0-100, "color": "#14C88C"}},
    {{"name": "Geographic consistency", "score": 0-100, "color": "#14C88C"}},
    {{"name": "Caption-visual match", "score": 0-100, "color": "#14C88C"}},
    {{"name": "Source credibility", "score": 0-100, "color": "#14C88C"}}
  ],
  "findings": [],
  "conclusion": "",
  "meta": {{}}
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1200,
    )

    raw = response.choices[0].message.content.strip()

    parsed = safe_extract_json(raw)

    return normalize_response(parsed)