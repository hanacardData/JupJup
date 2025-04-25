import pandas as pd
import requests

from bot.access_token import token_manager
from bot.message import get_message


def post_message(data: pd.DataFrame, is_test: bool = False) -> None:
    bot_id = 9881957  # 봇 ID; 고정
    test_channel_id = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"  # 테스트용 채널 ID
    base_url = (
        "https://www.worksapis.com/v1.0/bots/{bot_id}/channels/{channel_id}/messages"
    )
    channel_ids: list[str] = [
        "bf209668-eca1-250c-88e6-bb224bf9071a",
    ]  # 채널 ID; 추가할것
    token = token_manager.get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        message = get_message(data)
        message_payload = {
            "content": {
                "type": "text",
                "text": message,
            }
        }
        if is_test:
            url = base_url.format(bot_id=bot_id, channel_id=test_channel_id)
            requests.post(url, headers=headers, json=message_payload)
            return

        for channel_id in channel_ids:
            url = base_url.format(bot_id=bot_id, channel_id=channel_id)
            requests.post(url, headers=headers, json=message_payload)

    except Exception as e:
        error_message_payload = {
            "content": {
                "type": "text",
                "text": str(e),
            }
        }
        requests.post(
            base_url.format(bot_id=bot_id, channel_id=test_channel_id),
            headers=headers,
            json=error_message_payload,
        )
