import requests

from bot.access_token import token_manager
from bot.choose import select_post


def post_message() -> None:
    bot_id = 9881957  # 봇 ID; 고정
    channel_ids: list[str] = [
        "8895b3b4-1cff-cec7-b7bc-a6df449d3638",
        # "bf209668-eca1-250c-88e6-bb224bf9071a"
    ]  # 채널 ID; 추가할것
    token = token_manager.get_token()
    message = select_post()
    message_payload = {
        "content": {
            "type": "text",
            "text": message,
        }
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for channel_id in channel_ids:
        url = f"https://www.worksapis.com/v1.0/bots/{bot_id}/channels/{channel_id}/messages"
        requests.post(url, headers=headers, json=message_payload)


if __name__ == "__main__":
    post_message()
