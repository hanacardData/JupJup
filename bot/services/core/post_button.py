import httpx
from retry import retry

from bot.services.core.variables import CHANNEL_POST_URL
from bot.utils.access_token import set_headers
from logger import logger


def _set_button_payload() -> dict[str, dict[str, str]]:
    return {
        "content": {
            "type": "button_template",
            "contentText": "생성한 뉴스레터를 클릭해서 확인해보세요!",
            "actions": [
                {
                    "type": "message",
                    "label": "하나카드 이슈",
                    "text": "/이슈",
                },
                {
                    "type": "message",
                    "label": "트래블로그 이슈",
                    "text": "/트래블로그",
                },
                {
                    "type": "message",
                    "label": "트래블카드 트렌드 비교",
                    "text": "/트래블카드",
                },
            ],
        }
    }


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_button_message_to_channel(channel_id: str) -> None:
    headers = set_headers()
    template_payload = _set_button_payload()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=template_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise
