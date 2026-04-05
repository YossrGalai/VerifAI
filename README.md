# VerifAI — AI-Powered Misinformation Detector ✅

**Résumé:** VerifAI est un prototype full‑stack pour la détection de désinformation en ligne basé sur l'analyse multimodale (image + texte), la recherche d'image inversée et le raisonnement par IA. Le backend orchestre des agents spécialisés (extraction texte, OCR, recherche inversée, analyse contextuelle, raisonnement IA) et expose une API FastAPI ; le frontend React fournit une UI pour la soumission de contenu et la visualisation des verdicts.

## Aperçu
- Langages: **Python (backend)**, **TypeScript/React (frontend)**
- IA: **OpenAI API / Groq** (LLM pour le raisonnement)
- OCR: **Tesseract / EasyOCR**
- Recherche inversée: **SerpAPI / Bing Visual Search**
- Stockage: **SQLite** (optionnel, pour cache/historique)

---

## Architecture (vue d'ensemble)
┌─────────────────────────────────────────────────────────────┐
│ Frontend (React SPA) │
│ - UI, Upload image/URL, Affichage verdict │
│ - Services: api.service.ts pour communication │
└────────────────┬────────────────────────────────────────────┘
│ HTTP/REST
▼
┌─────────────────────────────────────────────────────────────┐
│ Backend API (Python FastAPI) │
│ - Orchestration (main.py, pipeline.py) │
│ - Agents: extraction, OCR, reverse_search, context, LLM │
│ - Services: raisonnement, analyse de cohérence │
│ - Logs d'analyse (JSONL) │
└────┬─────────────────────────────────────────────────┬──────┘
│ │
▼ ▼
┌─────────────────────┐ ┌──────────────────────┐
│ APIs externes │ │ Stockage local │
│ - SerpAPI │ │ - Images uploadées │
│ - OpenAI/Groq │ │ - Cache recherche │
│ - Bing Visual │ │ - Logs d'analyse │
└─────────────────────┘ └──────────────────────┘

text

## Fonctionnalités
- **Extraction intelligente** : Récupération d'image et texte depuis URL ou upload
- **OCR avancé** : Extraction texte depuis images (tesseract + easyocr)
- **Recherche inversée** : Traçabilité de l'origine des images (SerpAPI/Bing)
- **Analyse de contexte** : Détection d'incohérences temporelles/géographiques
- **Raisonnement IA** : LLM pour verdict final (Réel/Trompeur/Incertain)
- **Score de confiance** : Niveau de certitude (0-100%)
- **Explication détaillée** : Points spécifiques d'incohérence
- **Audit structuré** : JSONL pour traçabilité des analyses

## Pipeline de traitement
Soumission (URL ou image)
↓

Extraction

Si URL : scraping image + texte

Si image : OCR direct
↓

Recherche inversée

Origine source

Date publication originale

Contexte réel
↓

Analyse IA (Core)

Comparaison caption vs contexte réel

Détection incohérences
↓

Verdict final

Réel / Trompeur / Incertain

Score confiance

Explication structurée
↓

Audit & Logging

text

## Flux principal de fonctionnement

### 1. Analyse par URL
- Utilisateur soumet URL (Facebook, Twitter, etc.)
- Backend scrape la page : récupère image principale + texte
- OCR sur l'image (si texte présent)
- Recherche inversée de l'image
- LLM compare les informations
- Retour verdict + explication

### 2. Analyse par upload d'image
- Utilisateur upload une image + caption optionnel
- OCR extrait le texte de l'image
- Recherche inversée trouve l'origine
- LLM analyse la cohérence
- Retour verdict structuré

## Arborescence (fichiers clés)
verifai/
├── README.md # Ce fichier
├── requirements.txt # Dépendances Python
│
├── Backend/
│ ├── main.py # Point d'entrée FastAPI
│ ├── config.py # Configuration (API keys)
│ ├── app/
│ │ └── routes.py # Endpoints API
│ │
│ ├── core/
│ │ └── pipeline.py # Orchestration pipeline
│ │
│ ├── agents/ # Agents spécialisés
│ │ ├── extraction_agent.py # Extraction URL/image
│ │ ├── ocr_agent.py # OCR (Tesseract/EasyOCR)
│ │ ├── reverse_image_agent.py # Recherche inversée
│ │ ├── context_agent.py # Analyse contexte
│ │ ├── reasoning_agent.py # LLM raisonnement
│ │ └── audit_agent.py # Logging traçabilité
│ │
│ ├── services/ # Services métier
│ │ ├── url_service.py # Scraping URLs
│ │ ├── image_service.py # Traitement images
│ │ ├── llm_service.py # Appels OpenAI/Groq
│ │ └── cache_service.py # Cache résultats
│ │
│ ├── models/
│ │ └── schemas.py # Pydantic models
│ │
│ ├── uploads/ # Images uploadées
│ ├── logs/
│ │ └── analysis_log.jsonl # Logs d'analyses
│ │
│ ├── tests/ # Tests unitaires
│ │ ├── test_ocr.py
│ │ ├── test_reverse_image.py
│ │ ├── test_reasoning.py
│ │ └── test_pipeline.py
│ │
│ └── utils/
│ ├── logger.py # Logging utilitaire
│ └── validators.py # Validation entrées
│
├── frontend/
│ ├── package.json # Dépendances npm
│ ├── public/
│ │ └── index.html
│ └── src/
│ ├── App.js # Composant root
│ ├── index.js # Bootstrap
│ ├── services/
│ │ └── api.service.js # Communication backend
│ ├── components/
│ │ ├── UploadForm.jsx # Formulaire upload
│ │ ├── ResultDisplay.jsx # Affichage verdict
│ │ ├── ConfidenceGauge.jsx # Jauge confiance
│ │ └── ExplanationCard.jsx # Explications
│ └── styles/
│ └── App.css # Styles (Tailwind optionnel)
│
└── docs/
├── 00_Project_Vision.md # Vision projet
├── 01_Architecture.md # Architecture détaillée
├── 02_API_Documentation.md # Documentation API
└── 03_Demo_Scenarios.md # Scénarios démo

text

## Configuration

### Variables d'environnement (`.env`)
```bash
1) Backend setup
bash
cd Backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

pip install -r requirements.txt

2) Frontend setup
bash
cd frontend
npm install

Lancement local
1) Démarrer le backend
bash
cd Backend
uvicorn main:app --reload --port 8000
API disponible sur http://localhost:8000
Swagger UI: http://localhost:8000/docs

2) Démarrer le frontend
bash
cd frontend
npm start
SPA disponible sur http://localhost:3000

3) Vérifier les connexions
Backend API: http://localhost:8000/health

Frontend: http://localhost:3000

# API Endpoints
POST /analyze/url
Analyse une URL de média social

Request:

json
{
  "url": "https://twitter.com/user/status/123456789",
  "options": {
    "deep_search": true,
    "ocr_enabled": true
  }
}
Response:

json
{
  "verdict": "Misleading",
  "confidence_score": 87,
  "explanation": {
    "points": [
      "Image date de 2019 (inondation Pakistan)",
      "Caption prétend événement 2024 en France",
      "Contexte géographique incompatible"
    ],
    "conclusion": "L'image est réutilisée hors contexte pour tromper."
  },
  "metadata": {
    "analysis_time_ms": 2340,
    "image_source": "https://original.source.com/photo.jpg",
    "original_date": "2019-08-15"
  }
}
POST /analyze/image
Analyse une image uploadée

Request: multipart/form-data

image: fichier image

caption (optionnel): texte associé

GET /health
Vérification santé du service

## Tests
bash
# Tests unitaires OCR
python -m Backend.tests.test_ocr

# Tests recherche inversée
python -m Backend.tests.test_reverse_image

# Tests pipeline complet
python -m Backend.tests.test_pipeline

# Tous les tests
pytest Backend/tests/ -v
Démonstration (Cas d'usage)
✅ Cas 1: Contenu Réel
Input: Image tweet récent + caption cohérente

Verdict: Real (Confiance: 95%)

Explication: Image et contexte temporel/géographique correspondent

⚠️ Cas 2: Contenu Trompeur
Input: Vieille photo d'inondation + caption "Catastrophe aujourd'hui"

Verdict: Misleading (Confiance: 87%)

Explication: Image originale date de 2019 (Pakistan), caption prétend événement 2024 (France)

❓ Cas 3: Incertain
Input: Image ambiguë sans source claire

Verdict: Uncertain (Confiance: 45%)

Explication: Sources insuffisantes pour vérification définitive
