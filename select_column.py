from typing import Literal

import pandas as pd

COMMON_COLUMNS: list[str] = [
    "title",
    "link",
    "description",
    "source",
    "is_posted",
]


def _select_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[COMMON_COLUMNS + ["postdate"]].rename({"postdate": "post_date"}, axis=1)


def _select_news_data(data: pd.DataFrame) -> pd.DataFrame:
    _data = data[COMMON_COLUMNS + ["pubDate"]].rename({"pubDate": "post_date"}, axis=1)
    _data = _data.assign(
        post_date=pd.to_datetime(
            _data["post_date"], format="%a, %d %b %Y %H:%M:%S %z"
        ).dt.strftime("%Y%m%d"),
    )
    return _data


def _select_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[COMMON_COLUMNS].assign(post_date="")


SOURCES_SELECT_MAP: Literal["blog", "news", "cafe"] = {
    "blog": _select_blog_data,
    "news": _select_news_data,
    "cafe": _select_cafe_data,
}
