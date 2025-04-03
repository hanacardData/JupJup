import json
import os

from fetch import fetch_data
from queries import COMPETITORS

sources: list[str] = ["blog", "news", "cafe"]

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for source in sources:
        _file_path = os.path.join("data", f"{source}.json")
        if os.path.exists(_file_path):
            with open(_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data: dict[str, dict[str, str]] = {}

        for query in COMPETITORS:
            _data = fetch_data(
                type=source,
                query=query,
            )
            _items = _data.to_items()
            data.update({f"{query}_{_item['link']}": _item for _item in _items})

        with open(_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
