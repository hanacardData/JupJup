from bot.services.batch_message.utils import load_today_message_json


def get_travelcard_messages() -> list[str]:
    data = load_today_message_json()
    if not data:
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]

    return data.get("travelcard", ["트래블카드 메시지가 없습니다."])
