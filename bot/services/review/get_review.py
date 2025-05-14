from pathlib import Path

from bot.services.core.openai_client import async_openai_response

BASE_DIR = Path(__file__).parent
file_path = BASE_DIR / "prompt.json"
PROMPT_REVIEW = file_path.read_text(encoding="utf-8")


async def get_review_comment(input: str) -> str:
    return await async_openai_response(prompt=PROMPT_REVIEW, input=input)
