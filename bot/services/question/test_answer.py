# test_answer.py
import asyncio

from bot.services.question.get_answer import get_answer


async def main():
    response = await get_answer("부정적인 기사 총 정리해줘.")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
