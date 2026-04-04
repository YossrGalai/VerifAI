from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "VerifAI API running 🚀"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    return {
        "verdict": "Uncertain",
        "confidence": 50,
        "explanation": "Processing not implemented yet"
    }