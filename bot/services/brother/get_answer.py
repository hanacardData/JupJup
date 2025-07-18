from bot.services.brother.prompt import PROMPT
from bot.services.core.openai_client import async_openai_response


async def get_brother_answer(input: str) -> str:
    return await async_openai_response(
        prompt=PROMPT,
        input=input,
    )
