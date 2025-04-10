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


def _refine_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        ["title", "link", "description", "postdate", "source", "is_posted"]
    ].rename({"postdate": "post_date"}, axis=1)[SCHEMA]


def _refine_news_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        ["title", "link", "description", "pubDate", "source", "is_posted"]
    ].rename({"pubDate": "post_date"}, axis=1)[SCHEMA]


def _refine_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    return data[["title", "link", "description", "source", "is_posted"]].assign(
        post_date="",
    )[SCHEMA]


def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[data["is_posted"] == 0]


SOURCES_REFINE_MAP: Literal["blog", "news", "cafe"] = {
    "blog": _refine_blog_data,
    "news": _refine_news_data,
    "cafe": _refine_cafe_data,
}
