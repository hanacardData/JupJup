from typing import Callable

from fastapi.responses import JSONResponse

from bot.enums.default_messages import Message, NoneArgumentMessage
from bot.enums.status import BotStatus
from bot.services.catanddog.get_catanddog import get_cat, get_dog
from bot.services.compliment.get_compliment import get_compliment_comment
from bot.services.core.post_images import async_post_image_to_channel
from bot.services.core.post_message import (
    async_post_message_to_channel,
    async_post_template_message_to_channel,
)
from bot.services.fortune.get_fortune import get_fortune_comment
from bot.services.menu.get_menu import select_random_menu_based_on_weather
from bot.services.question.get_answer import get_answer_comment
from bot.services.review.get_review import get_review_comment


async def handle_help_command(channel_id: str) -> JSONResponse:
    """도움에 호출되는 핸들러입니다."""
    await async_post_message_to_channel(Message.GREETINGS_REPLY.value, channel_id)


async def handle_question_command(channel_id: str, argument: str):
    """질문을 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message_to_channel(
            NoneArgumentMessage.QUESTION.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )

    result = await get_answer_comment(argument)
    await async_post_message_to_channel(result, channel_id)


async def handle_menu_command(channel_id: str):
    """식당 추천을 요청했을 때 호출되는 핸들러입니다."""
    result = await select_random_menu_based_on_weather()
    await async_post_message_to_channel(result, channel_id)


async def handle_review_command(channel_id: str, argument: str):
    """리뷰를 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message_to_channel(
            NoneArgumentMessage.REVIEW.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_review_comment(argument)
    await async_post_message_to_channel(result, channel_id)


async def handle_fortune_command(channel_id: str, argument: str):
    """운세를 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message_to_channel(
            NoneArgumentMessage.FORTUNE.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_fortune_comment(argument)
    await async_post_message_to_channel(result, channel_id)


async def handle_compliment_command(channel_id: str, argument: str):
    """칭찬을 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message_to_channel(
            NoneArgumentMessage.COMPLIMENT.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_compliment_comment(argument)
    await async_post_message_to_channel(result, channel_id)


async def handle_cat_command(channel_id: str):
    """고양이 사진을 요청했을 때 호출되는 핸들러입니다."""
    result = await get_cat()
    await async_post_image_to_channel(result, channel_id)


async def handle_dog_command(channel_id: str):
    """강아지 사진을 요청했을 때 호출되는 핸들러입니다."""
    result = await get_dog()
    await async_post_image_to_channel(result, channel_id)


async def handle_jupjup_command(channel_id: str):
    await async_post_template_message_to_channel(channel_id)


COMMAND_HANDLERS: dict[str, Callable] = {  ## 커맨드 핸들러
    "/도움": handle_help_command,
    "/질문": handle_question_command,
    "/리뷰": handle_review_command,
    "/운세": handle_fortune_command,
    "/칭찬": handle_compliment_command,
    "/냥": handle_cat_command,
    "/멍": handle_dog_command,
    "/줍줍": handle_jupjup_command,
    "/식당": handle_menu_command,
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
        if command in ("/질문", "/리뷰", "/운세", "/칭찬"):
            await handler(channel_id, argument)
        else:
            await handler(channel_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )

    await async_post_message_to_channel(Message.UNKNOWN_COMMAND_REPLY.value, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.NO_COMMAND})
