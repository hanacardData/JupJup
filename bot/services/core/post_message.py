import httpx
import requests
from retry import retry

from bot.services.core.variables import CHANNEL_POST_URL, USER_POST_URL
from bot.utils.access_token import set_headers
from logger import logger


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
def post_message_to_channel(message: str, channel_id: str) -> None:
    message_payload = _set_messge_payload(message)
    headers = set_headers()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    try:
        response = requests.post(url, headers=headers, json=message_payload)
        response.raise_for_status()
        return
    except (requests.RequestException, requests.HTTPError) as e:
        logger.error(e)
        raise


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_message_to_channel(message: str, channel_id: str) -> None:
    message_payload = _set_messge_payload(message)
    headers = set_headers()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=message_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise


@retry(
    tries=3,
    delay=1,
    backoff=2,
    exceptions=(requests.RequestException, requests.HTTPError),
)
def post_message_to_user(message: str, user_id: str) -> None:
    message_payload = _set_messge_payload(message)
    headers = set_headers()
    url = USER_POST_URL.format(user_id=user_id)
    try:
        response = requests.post(url, headers=headers, json=message_payload)
        response.raise_for_status()
        return
    except (requests.RequestException, requests.HTTPError) as e:
        logger.error(e)
        raise


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_message_to_user(message: str, user_id: str) -> None:
    message_payload = _set_messge_payload(message)
    headers = set_headers()
    url = USER_POST_URL.format(user_id=user_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=message_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_template_message_to_channel(
    template_payload: dict, channel_id: str
) -> None:
    headers = set_headers()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url, headers=headers, json={"content": template_payload}
            )
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise
