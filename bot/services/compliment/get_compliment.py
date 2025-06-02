from bot.services.compliment.prompt import PROMPT
from bot.services.core.openai_client import async_openai_response


async def get_compliment_comment(input: str) -> str:
    result = await async_openai_response(
        prompt=PROMPT,
        input="멋지고 감동적인 솔직한 칭찬해줘!",
    )
    return input + "\n\n" + result
