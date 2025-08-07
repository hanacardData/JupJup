from bot.services.batch_message.utils import load_today_message_json

SUBKEY_MAP = {
    "/경쟁사신용": "신용카드 신상품",
    "/경쟁사체크": "체크카드 신상품",
    "/원더카드": "원더카드 고객반응",
    "/JADE": "JADE 고객반응",
}


def get_product_messages(subkey: str | None) -> list[str]:
    data = load_today_message_json()
    if not data:
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]

    label = SUBKEY_MAP.get(subkey)
    if not label:
        return ["지원하지 않는 상품 메시지 유형입니다."]

    return data.get("product", {}).get(label, ["해당 메시지가 없습니다."])
