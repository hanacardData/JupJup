import httpx
from retry import retry

from bot.services.core.variables import CHANNEL_POST_URL
from bot.utils.access_token import set_headers
from logger import logger


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_button_to_channel(
    payload: dict[str, dict[str, str | list[dict[str, str]]]],
    channel_id: str,
) -> None:
    headers = set_headers()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise
