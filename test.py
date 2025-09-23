from bot.services.core.openai_client import async_generate_image
from bot.services.core.post_images import async_post_image_to_channel


async def handle_generate_image_command(channel_id: str, argument: str):
    """이미지 생성을 요청했을 때 호출"""
    image_url = await async_generate_image(argument)
    await async_post_image_to_channel(image_url, channel_id)


if __name__ == "__main__":
    # Example usage
    import asyncio

    asyncio.run(
        handle_generate_image_command(
            "8895b3b4-1cff-cec7-b7bc-a6df449d3638",
            "귀여운 고양이가 스파르타 복장을 입고 있는 모습",
        )
    )
