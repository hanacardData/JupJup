import json
import os
from datetime import datetime
from typing import Literal


def get_batch_message(
    type_: Literal["issue", "travellog", "travelcard"],
) -> list[str]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("data", "messages", f"message_{today_str}.json")
    if not os.path.exists(output_file):
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[type_]
    except Exception as e:
        return [f"배치 메세지를 불러오는 중 오류가 발생했어요: {str(e)}"]
