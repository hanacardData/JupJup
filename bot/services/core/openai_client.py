from openai import APIConnectionError, APITimeoutError, AsyncOpenAI
from retry import retry

from logger import logger
from secret import OPENAI_API_KEY

async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def _make_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=OPENAI_API_KEY)


@retry(tries=3, delay=1, backoff=2, exceptions=APIConnectionError)
async def async_openai_response(
    prompt: str,
    input: str,
) -> str:
    try:
        response = await async_client.responses.create(
            model="gpt-4o",
            instructions=prompt,
            input=input,
            timeout=60,
        )
        return response.output_text.strip()
    except APIConnectionError as e:
        logger.error(e)
        raise


@retry(tries=5, delay=1, backoff=2, exceptions=(APIConnectionError, APITimeoutError))
async def async_generate_image(prompt: str) -> str | None:
    try:
        async with _make_client() as client:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                timeout=60,
            )
        return response.data[0].url
    except (APIConnectionError, APITimeoutError, Exception) as e:
        logger.error(e)
        return None
