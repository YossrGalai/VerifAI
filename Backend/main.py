from fastapi import FastAPI, UploadFile, File, Form
from core.pipeline import analyze_content

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "VerifAI API running 🚀"}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    caption: str = Form(...)
):
    result = await analyze_content(file, caption)
    return result