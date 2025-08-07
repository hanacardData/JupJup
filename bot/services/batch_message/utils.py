import json
import os
from datetime import datetime


def load_today_message_json() -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("data", "messages", f"message_{today_str}.json")
    if not os.path.exists(output_file):
        return {}

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
