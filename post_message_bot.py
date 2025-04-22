import requests

from access_token import token_manager
from choose import select_post


def post_message() -> None:
    bot_id = 9881957  # 봇 ID; 고정
    channel_ids: list[str] = [
        "8895b3b4-1cff-cec7-b7bc-a6df449d3638", 
        "bf209668-eca1-250c-88e6-bb224bf9071a"
    ]  # 채널 ID; 추가할것
    token = token_manager.get_token()
    message = select_post()
    message_payload = {
        "content": {
            "type": "link",
            "contentText": (
                "안녕하세요! 줍줍이입니다 🤗 \n제가 줍줍한 이슈를 공유드릴게요!\n\n"
                f"📌 제목: {message['title']}\n"
                f"📝 내용: {message['description']}\n"
            ),
            "linkText": "자세히 보기",
            "link": message["link"],
        }
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for channel_id in channel_ids:
        url = f"https://www.worksapis.com/v1.0/bots/{bot_id}/channels/{channel_id}/messages"
        requests.post(url, headers=headers, json=message_payload)


if __name__ == "__main__":
    post_message()
