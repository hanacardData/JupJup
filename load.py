"""
queries는 groupname: keywords 로 구성되도록 작성
참고: groupname은 키워드로 입력하지 않는 그룹명임
TODO: 키워드 추가 필요
"""

import os
from time import sleep

import pandas as pd

from fetch import fetch_data
from variables import DATA_PATH, QUERIES, SAVE_PATH, SOURCES


def _refine_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        ["title", "link", "description", "postdate", "source", "is_posted"]
    ].rename({"postdate": "post_date"}, axis=1)


def _refine_news_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        ["title", "link", "description", "pubDate", "source", "is_posted"]
    ].rename({"pubDate": "post_date"}, axis=1)


def _refine_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[["title", "link", "description", "source", "is_posted"]].assign(
        postDate="",
    )


SOURCES_REFINE_MAP = {
    "blog": _refine_blog_data,
    "news": _refine_news_data,
    "cafe": _refine_cafe_data,
}


def _read_csv(file_path: str) -> pd.DataFrame:
    if os.path.exists(file_path):
        return pd.read_csv(file_path, encoding="utf-8")
    return pd.DataFrame()


def collect_load_data(queries: dict[str, list[str]]) -> None:
    os.makedirs(SAVE_PATH, exist_ok=True)
    _df_list: list[pd.DataFrame] = [_read_csv(DATA_PATH)]
    for source in SOURCES:
        _file_path = os.path.join(SAVE_PATH, f"_{source}.csv")
        items: list[dict[str, str]] = []
        for _, keywords in queries.items():
            for keyword in keywords:
                _data = fetch_data(
                    type=source,
                    query=keyword,
                )
                sleep(0.5)
                _items = _data.to_items()
                items.extend(_items)

        _data_source = _read_csv(_file_path)
        _data_source = pd.concat(
            [_data_source, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])
        _data_source.to_csv(_file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_REFINE_MAP[source](_data_source))

    data = pd.concat(_df_list, ignore_index=True).sort_values(
        by="is_posted", ascending=False
    )
    data_deduplicated = data.drop_duplicates(subset="link", keep="first")
    data_deduplicated.to_csv(DATA_PATH, index=False, encoding="utf-8")


if __name__ == "__main__":
    collect_load_data(QUERIES)
