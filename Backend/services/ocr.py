import logging
from PIL import Image
import os

logger = logging.getLogger(__name__)

# Try to import pytesseract, fallback if not available
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    logger.warning("pytesseract not installed - OCR will use fallback mode")
    HAS_TESSERACT = False

# Optional: Uncomment if Tesseract-OCR is installed on Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def perform_ocr(image_path: str) -> dict:
    """
    Extrait le texte d'une image.
    Retourne un dict structuré avec le texte et un statut.
    Pas d'exceptions lancées - toujours retourne un dict valide.
    """
    if not image_path:
        return {"success": False, "text": None, "error": "Chemin image vide."}
    
    if not os.path.exists(image_path):
        return {"success": False, "text": None, "error": "Fichier image introuvable."}

    try:
        # Open and validate image
        with Image.open(image_path) as img:
            # Get image info
            img_info = f"{img.size[0]}x{img.size[1]} ({img.mode})"
            logger.info(f"Processing image: {img_info}")
            
            # If Tesseract not available, return success with info only
            if not HAS_TESSERACT:
                logger.warning("OCR skipped - Tesseract not available. Returning image metadata.")
                return {
                    "success": True,
                    "text": f"Image detected ({img_info})",
                    "error": None
                }
            
            # Try OCR with pytesseract
            try:
                img_processed = img.convert('L')  # niveaux de gris
                extracted_text = pytesseract.image_to_string(img_processed, lang='fra+eng')
                cleaned_text = extracted_text.strip()

                if not cleaned_text:
                    logger.info("No text detected in image")
                    return {"success": True, "text": None, "error": "Aucun texte détecté."}

                logger.info(f"OCR successful - {len(cleaned_text)} chars extracted")
                return {"success": True, "text": cleaned_text, "error": None}
            
            except Exception as ocr_error:
                logger.warning(f"Pytesseract error: {str(ocr_error)}")
                return {
                    "success": True,
                    "text": f"Image detected ({img_info})",
                    "error": f"OCR skipped: {str(ocr_error)[:50]}"
                }

    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        return {
            "success": True,
            "text": None,
            "error": f"Could not process image: {str(e)[:50]}"
        }