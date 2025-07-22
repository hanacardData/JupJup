import httpx
from retry import retry

from bot.services.core.variables import CHANNEL_POST_URL
from bot.utils.access_token import set_headers
from logger import logger


def _set_jupjup_button_payload() -> dict[str, dict[str, str]]:
    return {
        "content": {
            "type": "button_template",
            "contentText": "뉴스레터를 확인해보세요!",
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


def _set_lab_button_payload() -> dict[str, dict[str, str]]:
    return {
        "content": {
            "type": "button_template",
            "contentText": "실험실 기능을 테스트해보세요!",
            "actions": [
                {
                    "type": "message",
                    "label": "IMC 가이드에 맞춘 메시지 리뷰",
                    "text": "/리뷰",
                },
                {
                    "type": "message",
                    "label": "근처 식당 추천",
                    "text": "/식당",
                },
                {
                    "type": "message",
                    "label": "구내식당 메뉴 알리미",
                    "text": "/구내식당",
                },
                {
                    "type": "message",
                    "label": "사주팔자 기반의 운세",
                    "text": "/운세",
                },
                {
                    "type": "message",
                    "label": "나만의 충직한 동생과 대화해보세요!",
                    "text": "/아우야",
                },
            ],
        }
    }


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_jupjup_button_message_to_channel(channel_id: str) -> None:
    headers = set_headers()
    template_payload = _set_jupjup_button_payload()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=template_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise


@retry(tries=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPError))
async def async_post_lab_button_message_to_channel(channel_id: str) -> None:
    headers = set_headers()
    template_payload = _set_lab_button_payload()
    url = CHANNEL_POST_URL.format(channel_id=channel_id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=template_payload)
            response.raise_for_status()
            return
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(e)
            raise
