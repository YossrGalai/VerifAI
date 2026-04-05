# VerifAI — AI-Powered Misinformation Detector ✅

**Résumé**  
VerifAI est un prototype full-stack pour la détection de désinformation en ligne basé sur l'analyse multimodale (image + texte), la recherche d'image inversée et le raisonnement par IA. Le backend orchestre des composants spécialisés (OCR, recherche inversée, analyse contextuelle, raisonnement IA) et expose une API FastAPI ; le frontend React fournit une UI pour la soumission de contenu et la visualisation des verdicts.

## Aperçu
- Langages : **Python (backend)**, **JavaScript/React (frontend)**
- IA : **Groq / LLaMA** (LLM pour le raisonnement)
- OCR : **Tesseract via pytesseract**
- Recherche inversée : **SerpAPI**
- Stockage : fichiers locaux pour images uploadées / temporaires


## Fonctionnalités
- **Extraction intelligente** : traitement d’image uploadée ou URL
- **OCR avancé** : extraction de texte depuis image via Tesseract
- **Recherche inversée** : traçabilité de l’origine de l’image via SerpAPI
- **Analyse de contexte** : détection d’incohérences temporelles et de signaux suspects
- **Raisonnement IA** : LLM pour verdict final (`Réel` / `Trompeur` / `Incertain`)
- **Score de confiance** : estimation de certitude sur 0-100
- **Explication structurée** : points d’incohérence et notes de raisonnement

## Pipeline de traitement
1. Soumission (URL ou image)
2. Téléchargement / enregistrement temporaire
3. OCR sur l’image
4. Recherche inversée via SerpAPI
5. Construction du contexte
6. Appel LLM
7. Application de règles de raisonnement
8. Génération du verdict final
9. Retour de la réponse structurée

## Flux principal de fonctionnement

### Analyse par URL
- L’utilisateur soumet une URL d’image ou d’article
- Le backend télécharge l’image et scrape éventuellement l’article
- OCR sur l’image si nécessaire
- Recherche inversée sur l’image
- LLM compare caption / OCR / sources
- Retourne verdict + explication

### Analyse par upload d’image
- L’utilisateur upload une image et un caption optionnel
- OCR extrait le texte
- Recherche inversée détecte les sources
- LLM analyse la cohérence
- Retourne verdict structuré

## Arborescence (fichiers clés)


43 x 8
Je vérifie l’arborescence réelle et les fichiers frontend pour confirmer les écarts entre la réalité et le README.

Conclusion
Non, ton architecture actuelle ne correspond pas complètement à ton README actuel.

Écarts principaux
Backend/config.py n’existe pas.
Il n’y a pas de Backend/logs/analysis_log.jsonl.
Le frontend ne contient pas src/services/api.service.ts ni src/components/....
Il n’y a pas de dossier docs/ dans le repo.
SQLite n’est pas utilisé dans le code actuel.
La recherche inversée est implémentée uniquement via SerpAPI, pas Bing Visual Search.
Le backend utilise Groq/LLaMA via llm_service.py, mais pas de connexion OpenAI dans le code visible.
Version corrigée du README
Frontend (React SPA)

UI, upload image/URL, saisie de caption
Composant principal : App.js
Styles : App.css
HTTP/REST

Backend API (Python FastAPI)

Point d'entrée : main.py
Orchestration : pipeline.py
API route wrapper : routes.py
Services :
ocr.py
reverse_image.py
url_service.py
llm_service.py
reasoning_ai.py
source_detector.py
post_service.py
Modèles : schemas.py
.
├── README.md
├── requirements.txt
├── Backend/
│ ├── .env
│ ├── main.py
│ ├── api/
│ │ └── routes.py
│ ├── core/
│ │ └── pipeline.py
│ ├── models/
│ │ └── schemas.py
│ ├── services/
│ │ ├── context_service.py
│ │ ├── ocr.py
│ │ ├── reverse_image.py
│ │ ├── url_service.py
│ │ ├── llm_service.py
│ │ ├── reasoning_ai.py
│ │ ├── source_detector.py
│ │ └── post_service.py
│ ├── reverse_image.py
│ ├── test_ocr.png
│ ├── test_unit_context.py
│ ├── test_unit_ocr.py
│ ├── uploads/
│ └── venv/
├── frontend/
│ ├── package.json
│ ├── public/
│ │ └── index.html
│ └── src/
│ ├── App.js
│ ├── App.css
│ ├── index.js
│ ├── index.css
│ ├── App.test.js
│ ├── reportWebVitals.js
│ └── setupTests.js


## Configuration

### Backend
```bash
cd Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
