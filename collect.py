"""
파일 저장 구조를 현재는 dictionary 형태로
{f"하나카드_{글링크}": {정보}} 로 원천.json 형식으로 저장.
TODO: 저장할 방식 선택하여, 저장할 형식, 포맷 작성 필요함
"""

import json
import os

from fetch import fetch_data, fetch_trend_data
from queries import QUERIES

SOURCES: list[str] = ["blog", "news", "cafe"]
DATALAB_SOURCE: str = "datalab"
SAVE_PATH = "data"


def _read_json(file_path: str) -> dict[str, dict[str, str]]:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data: dict[str, dict[str, str]] = {}
    return data


if __name__ == "__main__":
    os.makedirs(SAVE_PATH, exist_ok=True)
    _datalab_file_path = os.path.join(SAVE_PATH, f"{DATALAB_SOURCE}.json")
    datalab_data = _read_json(_datalab_file_path)
    for group_name, keywords in QUERIES.items():
        _data = fetch_trend_data(
            startDate="2025-02-01",  # FIXME: 날짜 입력 수정 필요
            endDate="2025-02-28",  # FIXME: 날짜 입력 수정 필요
            timeUnit="date",
            keywordGroups=[{"groupName": group_name, "keywords": keywords}],
        )
        _results = _data.to_results()
        _key = _results[0].pop("title")
        datalab_data.update({_key: _results})

    with open(_datalab_file_path, "w", encoding="utf-8") as f:
        json.dump(datalab_data, f, ensure_ascii=False)

    for source in SOURCES:
        _file_path = os.path.join(SAVE_PATH, f"{source}.json")
        data = _read_json(_file_path)
        for group_name, keywords in QUERIES.items():
            for keyword in keywords:
                _data = fetch_data(
                    type=source,
                    query=keyword,
                )
                _items = _data.to_items()
                data.update(
                    {f"{group_name}_{_item['link']}": _item for _item in _items}
                )
        with open(_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
