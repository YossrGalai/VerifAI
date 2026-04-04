from app.services.ocr import perform_ocr
import os

# Chemin vers ton image de test
IMAGE_PATH = "test_ocr.png"

def test():
    print(f"--- Début du test OCR sur : {IMAGE_PATH} ---")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Erreur : L'image {IMAGE_PATH} n'existe pas dans le dossier.")
        return

    # Appel de ta fonction combinée
    resultat = perform_ocr(IMAGE_PATH)
    
    print("\n📝 Texte extrait :")
    print("-" * 30)
    print(resultat)
    print("-" * 30)
    
    if "Erreur" in resultat or "Échec" in resultat:
        print("\n❌ Le test a échoué. Vérifie le chemin de Tesseract.")
    elif "Aucun texte" in resultat:
        print("\n⚠️ Tesseract n'a rien lu. Essaie une image avec un texte plus net.")
    else:
        print("\n✅ Succès ! Ton module OCR est fonctionnel.")

if __name__ == "__main__":
    test()