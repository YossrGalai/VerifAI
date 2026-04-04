from typing import Optional

async def get_image_description(tmp_path: Optional[str]) -> str:

    if not tmp_path or not isinstance(tmp_path, str):
        return "No image provided"

    return "Image description from Dev 3 - not yet connected"