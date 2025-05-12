from bot.services.core.openai_client import async_openai_response


async def get_answer(input: str) -> str:
    return await async_openai_response(
        prompt="당신은 줍줍이라는 하나카드 회사의 챗봇입니다. 질문에 대한 답변을 간결하고 위트있게 존댓말로 답변합니다.",
        input=input,
    )
