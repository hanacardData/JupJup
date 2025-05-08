from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Callable

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from uvicorn.config import LOGGING_CONFIG

from bot.default_messages import GREETINGS_REPLY, PRIVATE_REPLY, UNKNOWN_COMMAND_REPLY
from bot.menu import select_random_menu_based_on_weather
from bot.openai_client import async_openai_response
from bot.post_message import async_post_message_to_channel, async_post_message_to_user
from bot.review import get_review_comment
from bot.utils import verify_signature
from logger import logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


class BotStatus(str, Enum):
    NO_COMMAND = "no_command"
    COMMAND_PROCESSED = "command_processed"
    ERROR = "error"
    IGNORED = "ignored"
    PRIVATE_REPLY_SENT = "private_reply_sent"
    MISSING_ARGUMENT = "missing_argument"
    GREETED = "greeted"


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


async def handle_review_command(channel_id: str, argument: str):
    if not argument:
        await async_post_message_to_channel("리뷰 내용을 입력해주세요!", channel_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_review_comment(argument)
    await async_post_message_to_channel(result, channel_id)


COMMAND_HANDLERS: dict[str, Callable] = {  ## 커맨드 핸들러
    "/도움": handle_help_command,
    "/질문": handle_question_command,
    "/식당": handle_menu_command,
    "/리뷰": handle_review_command,
}


async def handle_message_event(text: str, channel_id: str) -> JSONResponse:
    """메시지를 처리하는 핸들러입니다."""
    command_parts = text.split(maxsplit=1)
    command = command_parts[0]
    argument = command_parts[1] if len(command_parts) > 1 else ""
    if not command.startswith("/"):
        return JSONResponse(status_code=200, content={"status": BotStatus.IGNORED})

    handler = COMMAND_HANDLERS.get(command)
    if handler:
        if command in ("/질문", "/리뷰"):
            await handler(channel_id, argument)
        else:
            await handler(channel_id)
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

    if event_type == "join":
        # 채널에 봇이 추가되었을 때, user 대화에서는 join event가 발생하지 않음
        return await handle_join_event(channel_id=channel_id)

    if channel_id is None and user_id:  # 개인 대화에서 메세지를 받았을 때
        await async_post_message_to_user(PRIVATE_REPLY, user_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.PRIVATE_REPLY_SENT}
        )

    content = data.get("content", {})
    text = content.get("text", "")
    return await handle_message_event(text=text, channel_id=channel_id)


@app.post("/")
async def callback(
    request: Request, x_works_signature: str = Header(None)
) -> JSONResponse:
    """메시지 수신을 위한 메인 엔드포인트입니다."""
    raw_body = await request.body()
    raw_text = raw_body.decode()

    if not x_works_signature or not verify_signature(raw_text, x_works_signature):
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
