import json
import os
import re
from datetime import datetime
from typing import Literal


def get_batch_message(
    type_: Literal["issue", "travellog", "travelcard", "hanamoney", "hanapay"],
) -> list[str]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("data", "messages", f"message_{today_str}.json")
    if not os.path.exists(output_file):
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(type_, ["해당 메시지가 없습니다."])
    except Exception as e:
        return [f"배치 메세지를 불러오는 중 오류가 발생했어요: {str(e)}"]


def get_product_batch_message(
    subkey: Literal["/경쟁사신용", "/경쟁사체크", "/원더카드", "/JADE"],
) -> list[str]:
    """신상품 메시지만 처리하는 전용 함수"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("data", "messages", f"message_{today_str}.json")

    if not os.path.exists(output_file):
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("product", {}).get(subkey, ["해당 메시지가 없습니다."])
    except Exception as e:
        return [f"배치 메세지를 불러오는 중 오류가 발생했어요: {str(e)}"]


def make_travellog_flexible_payload(
    messages: list[str],
) -> dict[str, str | list[dict[str, str | list[dict[str, str]]]]]:
    carousel_payload = {"type": "carousel", "contents": []}

    for msg in messages[1:]:  # 첫 줄은 무시 (인사말)
        title_match = re.search(r"제목:\s*(.+)", msg)
        text_match = re.search(r"내용:\s*(.+)", msg)
        link_match = re.search(r"링크:\s*(.+)", msg)

        if not (title_match and text_match and link_match):
            continue
        title = title_match.group(1).strip('"{}').strip()
        text = text_match.group(1).strip('"{}').strip()
        link = link_match.group(1).strip('"{}').strip()
        content = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "contents": [{"type": "text", "text": title, "wrap": True}],
            },
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [{"type": "text", "text": text, "wrap": True}],
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {"type": "uri", "label": "link", "uri": link},
                        "height": "sm",
                    }
                ],
            },
        }
        carousel_payload["contents"].append(content)

    return {
        "content": {
            "type": "flex",
            "altText": "TravelLog",
            "contents": carousel_payload,
        }
    }


def make_app_review_flexible_payload(
    messages: list[str],
) -> dict[str, str | list[dict[str, str | list[dict[str, str]]]]]:
    carousel_payload = {"type": "carousel", "contents": []}

    for message in messages:
        text = message.strip('"{}').strip()
        content = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [{"type": "text", "text": text, "wrap": True}],
            },
        }
        carousel_payload["contents"].append(content)

    return {
        "content": {
            "type": "flex",
            "altText": "App Reviews",
            "contents": carousel_payload,
        }
    }
