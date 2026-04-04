from fastapi import APIRouter, UploadFile, File, Form
from core.pipeline import analyze_content

router = APIRouter()

@router.post("/analyze")
async def analyze(file: UploadFile = File(None), caption: str = Form(...)):
    result = await analyze_content(file, caption)
    return result