from bot.services.core.post_message import post_message_to_channel


async def send_scheduled_message(message: str, channel_id: str):
    await post_message_to_channel(message, channel_id)
