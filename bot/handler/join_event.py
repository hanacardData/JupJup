from fastapi.responses import JSONResponse

from bot.enums.default_messages import Message
from bot.enums.status import BotStatus
from bot.services.core.post_payload import async_post_message_to_channel


async def handle_join_event(channel_id: str) -> JSONResponse:
    """채널에 봇이 추가되었을 때나 도움요청에 호출되는 핸들러입니다."""
    await async_post_message_to_channel(Message.GREETINGS_REPLY.value, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.GREETED})
