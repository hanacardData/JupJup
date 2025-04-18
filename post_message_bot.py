import requests

from access_token import get_token

bot_id = 9881957
channel_id = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"
token = get_token()
message_payload = {
    "content": {"type": "text", "text": "안녕하세요! 물결 봇 테스트입니다."}
}
url = f"https://www.worksapis.com/v1.0/bots/{bot_id}/channels/{channel_id}/messages"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
response = requests.post(url, headers=headers, json=message_payload)
