from typing import Callable

from fastapi.responses import JSONResponse

from bot.enums.default_messages import Message
from bot.enums.status import BotStatus
from bot.services.core.openai_client import async_openai_response
from bot.services.core.post_message import async_post_message_to_channel
from bot.services.menu.get_menu import select_random_menu_based_on_weather
from bot.services.review.review import get_review_comment


async def handle_help_command(channel_id: str) -> JSONResponse:
    """채널에 봇이 추가되었을 때나 도움요청에 호출되는 핸들러입니다."""
    await async_post_message_to_channel(Message.GREETINGS_REPLY.value, channel_id)


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
    """f리뷰를 요청했을 때 호출되는 핸들러입니다."""
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

    await async_post_message_to_channel(Message.UNKNOWN_COMMAND_REPLY.value, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.NO_COMMAND})
