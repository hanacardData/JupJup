import httpx
from retry import retry

from bot.services.core.utils import set_headers
from bot.services.core.variables import CHANNEL_POST_URL
from logger import logger


def _set_image_payload(image_path: str) -> dict[str, dict[str, str]]:
    return {
        "content": {
            "type": "image",
            "previewImageUrl": image_path,
            "originalContentUrl": image_path,
        }
    }


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_image_to_channel(image_path: str, channel_id: str) -> None:
    image_payload = _set_image_payload(image_path)
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=set_headers(), json=image_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise
