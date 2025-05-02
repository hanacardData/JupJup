import base64
import hashlib
import hmac
from enum import Enum
from typing import Callable

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

from bot.menu import select_random_menu_based_on_weather
from bot.openai_client import async_openai_response
from bot.post_message import async_post_message_to_channel, async_post_message_to_user
from logger import logger
from secret import BOT_SECRET

app = FastAPI()


class BotStatus(str, Enum):
    NO_COMMAND = "no_command"
    COMMAND_PROCESSED = "command_processed"
    ERROR = "error"
    IGNORED = "ignored"
    PRIVATE_REPLY_SENT = "private_reply_sent"
    MISSING_ARGUMENT = "missing_argument"
    GREETED = "greeted"


GREETINGS_REPLY = """안녕하세요! 저는 줍줍이입니다. 😊
매일 주간 아침, 도움이 될 만한 고객의 소리를 수집해 전달해드려요.
뉴스레터를 받길 원하시면 대화방의 채널ID를 데이터사업부 김물결 주임 혹은 문상준 대리에게 보내주세요!

-궁금한 게 있거나 도움이 필요하실 땐 언제든지 "/질문 [질문]"으로 질문해주세요! 🐣
작은 궁금증도 제가 정성껏 알려드릴게요.

📝 사용 가능한 명령어 안내:
- /도움 : 사용할 수 있는 명령어를 알려드립니다.
- /질문 [질문] : 궁금한 내용을 입력해 주시면 답변드릴게요.
- /식당 : 뭐 드실지 고민이신가요? 식당을 추천해드려요!
"""

PRIVATE_REPLY = "안녕하세요. 저는 줍줍이 입니다. 현재는 1:1은 서비스 하고 있지 않습니다. 단체방을 이용해주세요!"
UNKNOWN_COMMAND_REPLY = "😅 알 수 없는 명령어입니다. '/도움'으로 도움말을 확인하세요."
ERROR_REPLY = "⚠️ 처리 중 오류가 발생했어요. 나중에 다시 시도해주세요. 만약 계속 오류가 발생한다면, 데이터 사업부 김물결 주임 혹은 문상준 대리에게 문의해주세요."


def _verify_signature(body: str, received_signature: str) -> bool:
    hash_digest = hmac.new(
        BOT_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash_digest).decode("utf-8")
    return hmac.compare_digest(signature, received_signature)


async def handle_join_event(channel_id: str) -> JSONResponse:
    """채널에 봇이 추가되었을 때 호출되는 핸들러입니다."""
    await async_post_message_to_channel(GREETINGS_REPLY, channel_id)
    logger.info(f"Sent greeting to channel {channel_id}")
    return JSONResponse(status_code=200, content={"status": BotStatus.GREETED})


async def handle_help_command(channel_id: str):
    """도움말을 요청했을 때 호출되는 핸들러입니다."""
    await async_post_message_to_channel(GREETINGS_REPLY, channel_id)


async def handle_question_command(channel_id: str, argument: str):
    """질문을 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message_to_channel(
            "질문 내용을 입력해주세요! 예: /질문 넌 누구니?", channel_id
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )

    result = await async_openai_response(
        prompt="당신은 줍줍이라는 하나카드 회사의 챗봇입니다. 질문에 대한 답변을 간결하고 위트있게 존댓말로 답변합니다.",
        input=argument,
    )
    await async_post_message_to_channel(result, channel_id)


async def handle_menu_command(channel_id: str):
    """식당 추천을 요청했을 때 호출되는 핸들러입니다."""
    result = await select_random_menu_based_on_weather()
    await async_post_message_to_channel(result, channel_id)


COMMAND_HANDLERS: dict[str, Callable] = {  ## 커맨드 핸들러
    "/도움": handle_help_command,
    "/질문": handle_question_command,
    "/식당": handle_menu_command,
}


async def handle_message_event(text: str, channel_id: str) -> JSONResponse:
    command_parts = text.split(maxsplit=1)
    command = command_parts[0]
    argument = command_parts[1] if len(command_parts) > 1 else ""

    handler = COMMAND_HANDLERS.get(command)
    if handler:
        await handler(channel_id, argument) if command == "/질문" else await handler(
            channel_id
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )

    await async_post_message_to_channel(UNKNOWN_COMMAND_REPLY, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.NO_COMMAND})


async def process_event(data: dict) -> JSONResponse:
    """이벤트를 처리하는 메인 핸들러입니다."""
    event_type = data.get("type")
    if event_type not in ["join", "message"]:
        logger.info(f"Ignored unsupported event type: {event_type}")
        return JSONResponse(status_code=200, content={"status": BotStatus.IGNORED})

    source = data["source"]
    channel_id = source.get("channelId")
    user_id = source.get("userId")

    if channel_id is None and user_id:
        await async_post_message_to_user(PRIVATE_REPLY, user_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.PRIVATE_REPLY_SENT}
        )

    if event_type == "join":
        return await handle_join_event(channel_id=channel_id)
    elif event_type == "message":
        content = data.get("content", {})
        text = content.get("text", "")
        return await handle_message_event(text=text, channel_id=channel_id)


# FastAPI 엔드포인트
@app.post("/")
async def callback(
    request: Request, x_works_signature: str = Header(None)
) -> JSONResponse:
    raw_body = await request.body()
    raw_text = raw_body.decode()

    if not x_works_signature or not _verify_signature(raw_text, x_works_signature):
        logger.warning("Invalid or missing signature.")
        raise HTTPException(status_code=403, detail="Invalid or missing signature")

    data = await request.json()
    return await process_event(data)


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    uvicorn.run("callback:app", host="0.0.0.0", port=5000, workers=4)
