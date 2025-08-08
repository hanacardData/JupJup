import json
import os
import re
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
            return data.get(type_, ["해당 메시지가 없습니다."])
    except Exception as e:
        return [f"배치 메세지를 불러오는 중 오류가 발생했어요: {str(e)}"]


def get_product_batch_message(subkey: str) -> list[str]:
    """신상품 메시지만 처리하는 전용 함수"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("data", "messages", f"message_{today_str}.json")

    if not os.path.exists(output_file):
        return ["배치 메세지를 위한 데이터를 수집하기 전이에요!"]

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            subkey_map = {
                "/경쟁사신용": "신용카드 신상품",
                "/경쟁사체크": "체크카드 신상품",
                "/원더카드": "원더카드 고객반응",
                "/JADE": "JADE 고객반응",
            }
            label = subkey_map.get(subkey)
            if label is None:
                return ["지원하지 않는 상품 메시지 유형입니다."]
            return data.get("product", {}).get(label, ["해당 메시지가 없습니다."])
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
        title = title_match.group(1).strip('"')
        text = text_match.group(1).strip('"')
        link = link_match.group(1).strip('"')
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
