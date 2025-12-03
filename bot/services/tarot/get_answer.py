from bot.services.core.openai_client import async_openai_response
from bot.services.tarot.prompt import PROMPT


async def get_tarot_answer(argument: str) -> str:
    """
    형식: [주제] [카드 번호들(콤마 구분)]
    """

    parts = argument.split(maxsplit=2)
    if len(parts) != 3:
        return (
            "타로 입력 형식이 올바르지 않습니다. '/타로 (주제) (선택할 카드 조합: 3개 또는 5개)'으로 입력해주세요.\n"
            "예) /타로 회사생활 14,16,33 또는 /타로 회사생활 14,16,33,71,1"
        )

    topic = parts[0]
    card_nums = parts[1]

    card_nums_list = [x.strip() for x in card_nums.split(",") if x.strip()]

    for card_num in card_nums_list:
        try:
            int(card_num)
        except ValueError:
            return "선택하실 카드의 종류는 숫자로 입력해주세요. 예) /타로 회사생활 3 14,16,33"

    formatted_input = (
        f"1) 주제: {topic}\n"
        f"2) 선택할 카드의 개수: {len(card_nums_list)}\n"
        f"3) 카드 번호: {', '.join(card_nums_list)}"
    )

    return await async_openai_response(
        prompt=PROMPT,
        input=formatted_input,
    )
