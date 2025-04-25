import pandas as pd
import requests

from bot.access_token import token_manager
from bot.message import get_issue_message

BOT_ID = 9881957


def _set_headers() -> dict[str, str]:
    token = token_manager.get_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def post_message_to_channel(message: str, channel_id: str) -> None:
    message_payload = {
        "content": {
            "type": "text",
            "text": message,
        }
    }
    headers = _set_headers()
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/channels/{channel_id}/messages"
    requests.post(url, headers=headers, json=message_payload)


def post_message_to_user(message: str, user_id: str) -> None:
    message_payload = {
        "content": {
            "type": "text",
            "text": message,
        }
    }
    headers = _set_headers()
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/users/{user_id}/messages"
    requests.post(url, headers=headers, json=message_payload)


def post_issue_message(data: pd.DataFrame, is_test: bool = False) -> None:
    test_channel_id = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"  # 테스트용 채널 ID
    channel_ids: list[str] = [
        "bf209668-eca1-250c-88e6-bb224bf9071a",  # 데이터 사업부
        "bb16f67c-327d-68e3-2e03-4215e67f8eb2",  # 물결님 동기
    ]  # 채널 ID; 추가할것

    try:
        message = get_issue_message(data)
        if is_test:
            post_message_to_channel(message, test_channel_id)
            return

        for channel_id in channel_ids:
            post_message_to_channel(message, channel_id)

    except Exception as e:
        post_message_to_channel(str(e), test_channel_id)
