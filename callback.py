import base64
import hashlib
import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request

from bot.issue import async_client
from bot.post_message import async_post_message_to_channel, async_post_message_to_user
from secret import BOT_SECRET

app = FastAPI()

# 답변 텍스트
JUPJUP_HELP_REPLY = """📝 사용 가능한 명령어:
- /줍줍help : 명령어 목록
- /줍줍qa [질문] : 질문에 대한 답변
"""

GREETINGS_REPLY = """안녕하세요! 저는 줍줍이입니다. 😊
매일 주간 아침, 도움이 될 만한 고객의 소리를 수집해 전달해드려요.

궁금한 게 있거나 도움이 필요하실 땐 언제든지 "/줍줍qa"로 질문해주세요! 🐣
작은 궁금증도 제가 정성껏 알려드릴게요.

📋 사용 가능한 명령어 안내:
/줍줍help : 사용할 수 있는 명령어를 알려드립니다.
/줍줍qa [질문] : 궁금한 내용을 입력해 주시면 답변드릴게요.
"""

PRIVATE_REPLY = "안녕하세요. 저는 줍줍이 입니다. 현재는 1:1은 서비스 하고 있지 않습니다. 단체방을 이용해주세요!"
UNKNOWN_COMMAND_REPLY = (
    "😅 알 수 없는 명령어입니다. '/줍줍help'로 도움말을 확인하세요.",
)


def _verify_signature(body: str, received_signature: str) -> bool:
    """요청 본문과 헤더의 X-WORKS-Signature를 비교"""
    hash_digest = hmac.new(
        BOT_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash_digest).decode("utf-8")
    return hmac.compare_digest(signature, received_signature)


@app.post("/")
async def callback(request: Request, x_works_signature: str = Header(None)):
    raw_body = await request.body()
    raw_text = raw_body.decode()

    if not _verify_signature(raw_text, x_works_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    event_type = data.get("type")

    if event_type == "join":
        channel_id = data["source"]["channelId"]
        await async_post_message_to_channel(GREETINGS_REPLY, channel_id)
        return {"status": "ok"}

    if event_type != "message":
        return {"status": "ok"}

    source = data["source"]
    content = data["content"]

    channel_id = source.get("channelId")
    user_id = source.get("userId")

    if channel_id is None and user_id:
        await async_post_message_to_user(PRIVATE_REPLY, user_id)
        return {"status": "ok"}

    text = content.get("text", "")

    if not text.startswith("/줍줍"):
        return {"status": "ok"}

    if text == "/줍줍help":
        await async_post_message_to_channel(JUPJUP_HELP_REPLY, channel_id)
    elif text.startswith("/줍줍qa"):
        question = text.replace("/줍줍qa", "").strip()
        response = await async_client.responses.create(
            model="gpt-4o",
            instructions="당신은 줍줍이라는 하나카드 회사의 챗봇입니다. 질문에 대한 답변을 간결하고 위트있게 존댓말로 답변합니다.",
            input=question,
        )
        result = response.output_text.strip()
        await async_post_message_to_channel(result, channel_id)
    else:
        await async_post_message_to_channel(UNKNOWN_COMMAND_REPLY, channel_id)

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("callback:app", host="0.0.0.0", port=5000, workers=4)
