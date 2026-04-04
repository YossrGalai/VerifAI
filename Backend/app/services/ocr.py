import pytesseract
from PIL import Image
import os
from dotenv import load_dotenv # [cite: 192]

# Charger les variables d'environnement (si besoin plus tard)
load_dotenv() 

# CONFIGURATION WINDOWS [cite: 80]
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def perform_ocr(image_path: str) -> str:
    """
    Extrait le texte d'une image de manière optimisée. [cite: 24, 115]
    """
    if not os.path.exists(image_path):
        return "Erreur : Le fichier image est introuvable."

    try:
        with Image.open(image_path) as img:
            # Conversion en niveaux de gris pour améliorer la détection [cite: 24]
            img_processed = img.convert('L')
            
            # Extraction du texte (Français + Anglais) [cite: 24]
            extracted_text = pytesseract.image_to_string(img_processed, lang='fra+eng')
            
            cleaned_text = extracted_text.strip()
            
            if not cleaned_text:
                return "Aucun texte détecté dans cette image."
                
            return cleaned_text

    except Exception as e:
        return f"Échec de l'OCR : {str(e)}"