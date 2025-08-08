from typing import Callable

import pandas as pd

SCHEMA: list[str] = [
    "query",
    "title",
    "link",
    "description",
    "post_date",
    "scrap_date",
    "source",
    "is_posted",
]


def _select_news_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.assign(post_date="")
    return df[SCHEMA]


def _select_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.rename(columns={"postdate": "post_date"})
    return df[SCHEMA]


SOURCES_SELECT_MAP: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "news": _select_news_data,
    "blog": _select_blog_data,
}
