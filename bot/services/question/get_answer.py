from bot.services.core.openai_client import async_openai_response
from bot.services.question.prompt import PROMPT


async def get_answer_comment(input: str) -> str:
    return await async_openai_response(
        prompt=PROMPT,
        input=input,
    )
