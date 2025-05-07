from typing import Callable

import pandas as pd

SCHEMA: list[str] = [
    "query",
    "title",
    "link",
    "description",
    "post_date",
    "source",
    "is_posted",
]


def _select_common_columns(data: pd.DataFrame, has_postdate: bool) -> pd.DataFrame:
    df = data.copy()
    if has_postdate:
        df = df.rename(columns={"postdate": "post_date"})
    else:
        df["post_date"] = ""

    return df[SCHEMA]


def _select_blog_data(data: pd.DataFrame) -> pd.DataFrame:
    return _select_common_columns(data, has_postdate=True)


def _select_cafe_data(data: pd.DataFrame) -> pd.DataFrame:
    return _select_common_columns(data, has_postdate=False)


SOURCES_SELECT_MAP: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "blog": _select_blog_data,
    "cafe": _select_cafe_data,
}
