from bot.openai_client import async_openai_response
from bot.prompt import PROMPT_REVIEW


async def get_review_comment(input: str) -> str:
    return await async_openai_response(prompt=PROMPT_REVIEW, input=input)
