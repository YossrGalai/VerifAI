from fastapi import APIRouter, UploadFile, File, Form, Request
from typing import Optional
from core.pipeline import run_pipeline

router = APIRouter()


@router.post("/analyze")
async def analyze(
    request: Request,
    file: Optional[UploadFile] = File(None),
    caption: str = Form(""),
):
    """
    Accepte deux formats :
    - multipart/form-data → file + caption
    - application/json → url + caption
    """

    content_type = request.headers.get("content-type", "").lower()

    # ── JSON MODE ─────────────────────────────────────
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            body = {}

        caption = body.get("caption", "")
        url = body.get("url", "")

        return await run_pipeline(file=None, caption=caption, url=url)

    # ── FORM MODE ─────────────────────────────────────
    return await run_pipeline(file=file, caption=caption, url=None)
