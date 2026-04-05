from typing import Optional

async def get_image_context(tmp_path: Optional[str] = None, url: Optional[str] = None) -> str:

    if url and isinstance(url, str):
        return f"URL provided: {url} — reverse search not connected"

    if tmp_path:
        return "Image context from Dev 3 Reverse Search - not yet connected"

    return "No image or URL provided"
