from fastapi.responses import JSONResponse

from bot.enums.default_messages import Message
from bot.enums.status import BotStatus
from bot.handler.message.channel import handle_message_event
from bot.services.core.post_payload import async_post_message
from logger import logger


async def handle_join_event(channel_id: str) -> JSONResponse:
    """채널에 봇이 추가되었을 때나 도움요청에 호출되는 핸들러입니다."""
    await async_post_message(Message.GREETINGS_REPLY.value, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.GREETED})


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
        await async_post_message(Message.PRIVATE_REPLY.value, user_id, True)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.PRIVATE_REPLY_SENT}
        )

    content = data.get("content", {})
    text = content.get("text", "")
    return await handle_message_event(text=text, channel_id=channel_id)
