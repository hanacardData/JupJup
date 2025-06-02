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
    "name",
    "is_posted",
]


def _select_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.rename(columns={"postdate": "post_date", "bloggername": "name"})
    return df[SCHEMA]


def _select_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.assign(post_date="").rename(columns={"cafename": "name"})
    return df[SCHEMA]


SOURCES_SELECT_MAP: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "blog": _select_blog_data,
    "cafe": _select_cafe_data,
}
