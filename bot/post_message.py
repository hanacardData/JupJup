import pandas as pd
import requests

from bot.access_token import token_manager
from bot.message import get_message

BOT_ID = 9881957


def post_message_to_channel(message: str, channel_id: str) -> None:
    token = token_manager.get_token()
    message_payload = {
        "content": {
            "type": "text",
            "text": message,
        }
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/channels/{channel_id}/messages"
    requests.post(url, headers=headers, json=message_payload)


def post_message_to_user(message: str, user_id: str) -> None:
    token = token_manager.get_token()
    message_payload = {
        "content": {
            "type": "text",
            "text": message,
        }
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/users/{user_id}/messages"
    requests.post(url, headers=headers, json=message_payload)


def post_message(data: pd.DataFrame) -> None:
    channel_ids: list[str] = [
        "8895b3b4-1cff-cec7-b7bc-a6df449d3638",  # for test
        "bf209668-eca1-250c-88e6-bb224bf9071a",
    ]  # 채널 ID; 추가할것
    message = get_message(data)
    for channel_id in channel_ids:
        post_message_to_channel(message, channel_id)
