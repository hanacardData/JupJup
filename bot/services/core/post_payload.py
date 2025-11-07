from typing import Any

import httpx
import requests
from retry import retry

from bot.utils.access_token import set_headers
from logger import logger

CHANNEL_POST_URL = "https://www.worksapis.com/v1.0/bots/9881957/channels/{id}/messages"
USER_POST_URL = "https://www.worksapis.com/v1.0/bots/9881957/users/{id}/messages"


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_payload(
    payload: dict[str, Any],
    id: str,
    base: str = CHANNEL_POST_URL,
) -> None:
    headers = set_headers()
    url = base.format(id=id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise


def _set_messge_payload(message: str) -> dict[str, dict[str, str]]:
    return {
        "content": {
            "type": "text",
            "text": message,
        }
    }


@retry(
    tries=3,
    delay=1,
    backoff=2,
    exceptions=(requests.RequestException, requests.HTTPError),
)
def post_message_to_channel(message: str, channel_id: str) -> None:  # FIXME: deprecated
    message_payload = _set_messge_payload(message)
    headers = set_headers()
    url = CHANNEL_POST_URL.format(id=channel_id)
    try:
        response = requests.post(url, headers=headers, json=message_payload)
        response.raise_for_status()
        return
    except (requests.RequestException, requests.HTTPError) as e:
        logger.error(e)
        raise


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_message(message: str, id: str, is_user: str = False) -> None:
    message_payload = _set_messge_payload(message)
    await async_post_payload(
        message_payload, id, base=USER_POST_URL if is_user else CHANNEL_POST_URL
    )


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
    await async_post_payload(image_payload, channel_id)
    return
