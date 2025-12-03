from bot.services.core.openai_client import async_openai_response
from bot.services.tarot.prompt import PROMPT


async def get_tarot_answer(argument: str) -> str:
    """
    형식: [주제] [카드 개수] [카드 번호들(콤마 구분)]
    """

    parts = argument.split(maxsplit=2)
    if len(parts) != 3:
        return (
            "타로 입력 형식이 올바르지 않습니다. '/타로 (주제) (카드개수) (선택할 카드 조합)'으로 입력해주세요.\n"
            "예) /타로 회사생활 3 14,16,33"
        )

    topic = parts[0]
    how_many = parts[1]
    card_nums = parts[2]

    if how_many not in ("3", "5"):
        return "카드 개수는 3 또는 5만 가능합니다. 예) /타로 회사생활 3 14,16,33"

    try:
        how_many_int = int(how_many)
    except ValueError:
        return "카드 개수는 숫자로 입력해주세요. 예) /타로 회사생활 3 14,16,33"

    card_nums_list = [x.strip() for x in card_nums.split(",") if x.strip()]

    if len(card_nums_list) != how_many_int:
        return (
            "선택한 카드 개수와 카드 번호 개수가 맞지 않습니다.\n"
            f"입력한 카드 수: {how_many_int}장, 번호 개수: {len(card_nums_list)}개\n"
            "예) /타로 회사생활 3 14,16,33  (3장 → 번호 3개)"
        )
    for card_num in card_nums_list:
        try:
            card_num_int = int(card_num)
            del card_num_int
        except ValueError:
            return "선택하실 카드의 종류는 숫자로 입력해주세요. 예) /타로 회사생활 3 14,16,33"

    formatted_input = (
        f"1) 주제: {topic}\n"
        f"2) 선택할 카드의 개수: {how_many_int}\n"
        f"3) 카드 번호: {', '.join(card_nums_list)}"
    )

    return await async_openai_response(
        prompt=PROMPT,
        input=formatted_input,
    )
