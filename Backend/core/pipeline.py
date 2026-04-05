import os
import shutil
import tempfile
from fastapi import UploadFile
from typing import Optional
from services.image_service import get_image_description
from services.context_service import get_image_context
from services.llm_service import get_llm_verdict


async def run_pipeline(
    file: Optional[UploadFile],
    caption: str,
    url: Optional[str] = None,
) -> dict:

    tmp_path = None

    # ── SAVE FILE ───────────────────────────────
    if file is not None:
        suffix = os.path.splitext(file.filename or "")[-1] or ".jpg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            if file.file:
                shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

    try:
        image_description = await get_image_description(tmp_path)
        image_context = await get_image_context(tmp_path=tmp_path, url=url)

        result = await get_llm_verdict(
            caption=caption,
            image_description=image_description,
            image_context=image_context,
        )

        return result

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
