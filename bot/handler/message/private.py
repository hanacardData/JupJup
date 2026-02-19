from agents import Runner
from fastapi.responses import JSONResponse

from bot.enums.default_messages import Message
from bot.enums.status import BotStatus
from bot.handler.message.agent import agent
from bot.services.core.post_payload import (
    async_post_message,
)
from logger import logger


async def handle_private_message_event(text: str, user_id: str) -> JSONResponse:
    try:
        result = await Runner.run(agent, text)
        response = result.final_output
    except Exception as e:
        logger.exception(f"handle private agent exception: {e}")
        response = Message.ERROR_REPLY.value

    await async_post_message(response, user_id, True)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.PRIVATE_REPLY_SENT}
    )
