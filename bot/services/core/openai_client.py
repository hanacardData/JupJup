from acachetools import cached
from cachetools import TTLCache
from openai import APIConnectionError, AsyncOpenAI
from retry import retry

from logger import logger
from secret import OPENAI_API_KEY

async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def async_openai_response(
    prompt: str,
    input: str,
    timeout: int = 60,
    max_retries: int = 5,
    initial_delay: int = 1,
    backoff_factor: int = 2,
) -> str:
    @retry(
        tries=max_retries,
        delay=initial_delay,
        backoff=backoff_factor,
        exceptions=(APIConnectionError, TimeoutError),
    )
    async def _execute():
        try:
            response = await async_client.responses.create(
                model="gpt-4o",
                instructions=prompt,
                input=input,
                timeout=timeout,
            )
            return response.output_text.strip()
        except (APIConnectionError, TimeoutError) as e:
            logger.warning(f"Retry exceptions: {type(e).__name__} - {e}")
            raise
        except Exception as e:
            logger.error(f"Something wrong: {type(e).__name__} - {e}")
            raise

    return await _execute()


@retry(tries=5, delay=1, backoff=2, exceptions=APIConnectionError)
@cached(TTLCache(maxsize=100, ttl=3600))
async def async_generate_image(prompt: str) -> str | None:
    response = await async_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    if response and response.data and len(response.data) > 0:
        return response.data[0].url
    return None
