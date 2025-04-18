from typing import Literal

import pandas as pd

SCHEMA: list[str] = [
    "title",
    "link",
    "description",
    "post_date",
    "source",
    "is_posted",
]


def _select_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        ["title", "link", "description", "postdate", "source", "is_posted"]
    ].rename({"postdate": "post_date"}, axis=1)[SCHEMA]


def _select_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[["title", "link", "description", "source", "is_posted"]].assign(
        post_date="",
    )[SCHEMA]


SOURCES_SELECT_MAP: Literal["blog", "news", "cafe"] = {
    "blog": _select_blog_data,
    "cafe": _select_cafe_data,
}
