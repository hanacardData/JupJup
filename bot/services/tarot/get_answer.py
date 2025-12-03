from bot.services.core.openai_client import async_openai_response
from bot.services.tarot.prompt import PROMPT


async def get_tarot_answer(topic: str, card_nums: str) -> str:
    if topic == "":
        return "입력하신 주제를 확인해주세요. 예) /타로 회사생활 14,16,33"
    if card_nums == "":
        return "입력하신 카드 숫자를 확인해주세요. 예) /타로 회사생활 14,16,33"

    card_nums_list = [x.strip() for x in card_nums.split(",") if x.strip()]
    for card_num in card_nums_list:
        try:
            int(card_num)
        except ValueError:
            return "선택하실 카드의 종류는 숫자로 입력해주세요. 예) /타로 회사생활 14,16,33"

    formatted_input = (
        f"1) 주제: {topic}\n"
        f"2) 선택할 카드의 개수: {len(card_nums_list)}\n"
        f"3) 카드 번호: {', '.join(card_nums_list)}"
    )

    return await async_openai_response(
        prompt=PROMPT,
        input=formatted_input,
    )
