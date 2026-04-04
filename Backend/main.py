from fastapi import FastAPI, UploadFile, File, Form
from core.pipeline import analyze_content
from fastapi import FastAPI, UploadFile, File
from Backend.app.services.ocr import extract_text_from_image
from reverse_image import reverse_image_search
import openai
import shutil
import os
import random

openai.api_key = "VOTRE_OPENAI_API_KEY"

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/verify_content/")
async def verify_content(file: UploadFile = File(...)):
    # Sauvegarder l'image uploadée
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # OCR
    extracted_text = extract_text_from_image(file_path)

    # Reverse image
    reverse_results = reverse_image_search(file_path)

    # Score de confiance simulé
    confidence_score = round(random.uniform(0, 1), 2)  # entre 0 et 1

    # Préparer JSON pour LLM
    structured_data = {
        "source_type": "image",
        "original_text": extracted_text,
        "reverse_image_results": reverse_results,
        "confidence_score": confidence_score
    }

    # Interroger OpenAI pour résumé
    prompt = f"""
    Voici le texte extrait d'une image et ses résultats de recherche inversée :
    {structured_data}
    Vérifie si le contenu est fiable et donne un résumé clair en 2 phrases.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    llm_result = response['choices'][0]['message']['content']

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    caption: str = Form(...)
):
    result = await analyze_content(file, caption)
    return result
    return {
        "structured_data": structured_data,
        "llm_analysis": llm_result
    }
