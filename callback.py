import base64
import hashlib
import hmac

from flask import Flask, jsonify, request

from bot.message import client
from bot.post_message import post_message_to_channel, post_message_to_user
from secret import BOT_SECRET

app = Flask(__name__)

jupjup_help_reply = """📝 사용 가능한 명령어:
- /줍줍help : 명령어 목록
- /줍줍qa [질문] : 질문에 대한 답변
"""

greetings_reply = """안녕하세요! 저는 줍줍이입니다. 😊
매일 주간 아침, 도움이 될 만한 고객의 소리를 수집해 전달해드려요.

궁금한 게 있거나 도움이 필요하실 땐 언제든지 "/줍줍qa"로 질문해주세요! 🐣
작은 궁금증도 제가 정성껏 알려드릴게요.

📋 사용 가능한 명령어 안내:
/줍줍help : 사용할 수 있는 명령어를 알려드립니다.
/줍줍qa [질문] : 궁금한 내용을 입력해 주시면 답변드릴게요.
"""


def _verify_signature(body: str, received_signature: str) -> bool:
    """요청 본문과 헤더의 X-WORKS-Signature를 비교"""
    hash_digest = hmac.new(
        BOT_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash_digest).decode("utf-8")
    return hmac.compare_digest(signature, received_signature)


@app.route("/", methods=["POST"])
def callback():
    raw_body = request.get_data(as_text=True)
    headers_signature = request.headers.get("X-WORKS-Signature")
    if not _verify_signature(raw_body, headers_signature):
        return jsonify({"error": "Invalid signature"}), 403

    json_data = request.get_json()
    _type = json_data["type"]

    if _type == "join":
        channel_id = json_data["source"]["channelId"]
        post_message_to_channel(greetings_reply, channel_id)
        return jsonify({"status": "ok"})

    if _type != "message":
        return jsonify({"status": "ok"})

    channel_id = json_data["source"].get("channelId", None)
    if channel_id is None:
        user_id = json_data["source"].get("userId", None)
        post_message_to_user(
            "안녕하세요. 저는 줍줍이 입니다. 현재는 1:1은 서비스 하고 있지 않습니다. 단체방을 이용해주세요!",
            user_id,
        )

    text = json_data["content"]["text"]
    if not text.startswith("/줍줍"):
        return jsonify({"status": "ok"})

    if text == "/줍줍help":
        post_message_to_channel(jupjup_help_reply, channel_id)
        return jsonify({"status": "ok"})
    elif text.startswith("/줍줍qa"):
        question = text.replace("/줍줍qa", "").strip()
        response = client.responses.create(
            model="gpt-4o",
            instructions="당신은 줍줍이라는 하나카드 회사의 챗봇입니다. 질문에 대한 답변을 간결하고 위트있게 존댓말로 답변합니다.",
            input=question,
        )
        result = response.output_text.strip()
        post_message_to_channel(result, channel_id)
        return jsonify({"status": "ok"})
    # TODO: 줍줍 메뉴 추천 기능 추가
    else:
        reply = "😅 알 수 없는 명령어입니다. '/줍줍help'로 도움말을 확인하세요."
        post_message_to_channel(reply, channel_id)
        return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000)
