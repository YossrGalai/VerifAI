from services.image_service import get_image_description
from services.context_service import get_image_context
from services.llm_service import analyze_with_llm

async def analyze_content(file, caption):

    image = await get_image_description(file)
    context = await get_image_context(file)

    result = await analyze_with_llm(
        caption,
        image["image_description"],
        context["real_context"]
    )

    return result