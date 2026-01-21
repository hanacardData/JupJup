import asyncio
from typing import Callable

from fastapi.responses import JSONResponse

from bot.enums.button_templates import JUPJUP_BUTTON, LAB_BUTTON, PRODUCT_BUTTON
from bot.enums.default_messages import Message, NoneArgumentMessage
from bot.enums.status import BotStatus
from bot.services.batch_message.get_message import (
    get_batch_message,
    get_product_batch_message,
    make_app_review_flexible_payload,
    make_flexible_payload,
    make_geeknews_payload,
)
from bot.services.brother.get_answer import get_brother_answer
from bot.services.cafeteria.menu import get_weekly_menu_message
from bot.services.core.openai_client import async_generate_image
from bot.services.core.post_payload import (
    async_post_image,
    async_post_message,
    async_post_payload,
)
from bot.services.fortune.get_fortune import get_fortune_comment
from bot.services.harmony.get_harmony import get_harmony_comment
from bot.services.tarot.get_answer import get_tarot_answer


async def handle_help_command(channel_id: str) -> JSONResponse:
    """도움에 호출되는 핸들러입니다."""
    await async_post_message(Message.GREETINGS_REPLY.value, channel_id)


async def handle_travellog_command(channel_id: str) -> JSONResponse:
    """트래블로그를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("travellog")
    if len(messages) == 1:
        await async_post_message(messages[0], channel_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )
    payload = make_flexible_payload(messages)
    await async_post_payload(payload, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_issue_command(channel_id: str) -> JSONResponse:
    """이슈를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("issue")
    for message in messages:
        await async_post_message(message, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_travelcard_command(channel_id: str) -> JSONResponse:
    """트래블카드를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("travelcard")
    for message in messages:
        await async_post_message(message, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def _handle_product_command(channel_id: str, subkey: str) -> JSONResponse:
    messages = get_product_batch_message(subkey=subkey)
    for message in messages:
        await async_post_message(message, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_product_credit_command(channel_id: str) -> JSONResponse:
    return await _handle_product_command(channel_id, "/경쟁사신용")


async def handle_product_debit_command(channel_id: str) -> JSONResponse:
    return await _handle_product_command(channel_id, "/경쟁사체크")


async def handle_product_wonder_command(channel_id: str) -> JSONResponse:
    return await _handle_product_command(channel_id, "/원더카드")


async def handle_product_jade_command(channel_id: str) -> JSONResponse:
    return await _handle_product_command(channel_id, "/JADE")


async def handle_cafeteria_command(channel_id: str) -> JSONResponse:
    """구내식당 식단을 요청했을 때 호출되는 핸들러입니다."""
    message = get_weekly_menu_message()
    await async_post_message(message, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_brother_command(channel_id: str, argument: str) -> JSONResponse:
    """아우야를 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message(
            NoneArgumentMessage.BROTHER.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )

    result = await get_brother_answer(argument)
    await async_post_message(result, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_fortune_command(channel_id: str, argument: str) -> JSONResponse:
    """운세를 요청했을 때 호출되는 핸들러입니다."""
    if not argument:
        await async_post_message(
            NoneArgumentMessage.FORTUNE.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_fortune_comment(argument)
    await async_post_message(result, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_harmony_command(
    channel_id: str, argument: str, sub_argument: str
) -> JSONResponse:
    """궁합을 요청했을 때 호출되는 핸들러입니다."""
    if not argument or not sub_argument:
        await async_post_message(
            NoneArgumentMessage.HARMONY.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    result = await get_harmony_comment(argument, sub_argument)
    await async_post_message(result, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_generate_image_command(channel_id: str, argument: str) -> JSONResponse:
    """이미지 생성을 요청했을 때 호출"""
    if not argument:
        await async_post_message(
            NoneArgumentMessage.IMAGE_GENERATION_REPLY.value, channel_id
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )
    image_url = await async_generate_image(argument)
    if image_url:
        await async_post_image(image_url, channel_id)
    else:
        await async_post_message(
            "이미지 생성에 실패했습니다. 다시 시도해주세요.", channel_id
        )
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_hanamoney_command(channel_id: str) -> JSONResponse:
    """하나머니를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("hanamoney")
    if len(messages) == 0:
        await async_post_message(
            "최근 3일 이내에 하나머니 앱 리뷰가 없습니다.", channel_id
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )

    payload = make_app_review_flexible_payload(messages)
    await async_post_payload(payload, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_hanapay_command(channel_id: str) -> JSONResponse:
    """하나페이를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("hanapay")
    if len(messages) == 0:
        await async_post_message(
            "최근 3일 이내에 하나페이 앱 리뷰가 없습니다.", channel_id
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )

    payload = make_app_review_flexible_payload(messages)
    await async_post_payload(payload, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_security_command(channel_id: str) -> JSONResponse:
    """보안이슈를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("security")
    if not messages:
        await async_post_message(
            "오늘은 보안과 관련한 주목할만한 이슈가 없어요! 다음에 더 좋은 이슈로 찾아올게요 😊",
            channel_id,
        )
    else:
        await async_post_payload(make_flexible_payload(messages), channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_geeknews_command(channel_id: str) -> JSONResponse:
    """긱뉴스를 요청했을 때 호출되는 핸들러입니다."""
    messages = get_batch_message("geeknews")
    if len(messages) > 1:
        payload = make_geeknews_payload(messages)
        await async_post_payload(payload, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_jupjup_command(channel_id: str) -> JSONResponse:
    """줍줍 핸들러"""
    await async_post_payload(JUPJUP_BUTTON, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_lab_command(channel_id: str) -> JSONResponse:
    """실험실 핸들러"""
    await async_post_payload(LAB_BUTTON, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_product_command(channel_id: str) -> JSONResponse:
    """신규 상품 핸들러"""
    await async_post_payload(PRODUCT_BUTTON, channel_id)
    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


async def handle_tarot_command(
    channel_id: str, argument1: str, argument2: str
) -> JSONResponse:
    """타로를 요청했을 때 호출되는 핸들러입니다."""
    if not argument1 or not argument2:
        await async_post_message(
            NoneArgumentMessage.TAROT.value,
            channel_id,
        )
        return JSONResponse(
            status_code=200, content={"status": BotStatus.MISSING_ARGUMENT}
        )

    async def send_progress_messages():
        await async_post_message("🔮 기운을 모으는 중이에요", channel_id)
        await asyncio.sleep(3)
        await async_post_message("✨ 흐름이 잡혀가고 있어요", channel_id)
        await asyncio.sleep(3)
        await async_post_message("🌙 방향을 정리하고 있어요", channel_id)

    asyncio.create_task(send_progress_messages())

    result = await get_tarot_answer(argument1, argument2)

    await async_post_message(result, channel_id)

    return JSONResponse(
        status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
    )


COMMAND_HANDLERS: dict[str, Callable] = {  ## 커맨드 핸들러
    # 명령 커맨드
    "/도움": handle_help_command,
    "/줍줍": handle_jupjup_command,
    "/실험실": handle_lab_command,
    # Argument 없는 커맨드
    "/트래블로그": handle_travellog_command,
    "/이슈": handle_issue_command,
    "/트래블카드": handle_travelcard_command,
    "/경쟁사신용": handle_product_credit_command,
    "/경쟁사체크": handle_product_debit_command,
    "/원더카드": handle_product_wonder_command,
    "/JADE": handle_product_jade_command,
    "/구내식당": handle_cafeteria_command,
    "/신상품": handle_product_command,
    "/하나머니": handle_hanamoney_command,
    "/하나페이": handle_hanapay_command,
    "/보안": handle_security_command,
    "/긱뉴스": handle_geeknews_command,
    # Argument 필요한 커맨드
    "/아우야": handle_brother_command,
    "/운세": handle_fortune_command,
    "/궁합": handle_harmony_command,
    "/이미지": handle_generate_image_command,
    "/타로": handle_tarot_command,
}


async def handle_message_event(text: str, channel_id: str) -> JSONResponse:
    """메시지를 처리하는 핸들러입니다."""
    if not text.startswith("/"):
        return JSONResponse(status_code=200, content={"status": BotStatus.IGNORED})

    command_parts = text.split(maxsplit=1)
    command = command_parts[0]
    argument = command_parts[1] if len(command_parts) > 1 else ""
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        if command in ("/아우야", "/운세", "/이미지"):
            await handler(channel_id, argument)
        elif command in ("/궁합", "/타로"):
            try:
                argument_parts = argument.split(maxsplit=1)
                argument1 = argument_parts[0]
                argument2 = argument_parts[1]
            except Exception:
                argument1 = ""
                argument2 = ""
            await handler(channel_id, argument1, argument2)
        else:
            await handler(channel_id)
        return JSONResponse(
            status_code=200, content={"status": BotStatus.COMMAND_PROCESSED}
        )

    await async_post_message(Message.UNKNOWN_COMMAND_REPLY.value, channel_id)
    return JSONResponse(status_code=200, content={"status": BotStatus.NO_COMMAND})
