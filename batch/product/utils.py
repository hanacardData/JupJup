from email.utils import parsedate_to_datetime
from typing import Optional

import pandas as pd


def to_yyyymmdd_str(x: Optional[str]) -> Optional[str]:
    if x is None or (isinstance(x, str) and x.strip() == ""):
        return pd.NA
    dt = pd.to_datetime(x, errors="coerce")
    if pd.isna(dt):
        try:
            dt = parsedate_to_datetime(str(x))
        except Exception:
            return pd.NA
    return dt.strftime("%Y%m%d")


def ensure_string_col(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col not in df.columns:
        df[col] = pd.NA
    try:
        df[col] = df[col].astype("string")
    except Exception:
        df[col] = df[col].astype(object)
    return df


def sanitize_postdate(df: pd.DataFrame, col: str = "postdate") -> pd.DataFrame:
    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .where(lambda s: s.str.len() == 8, "")
    )
    return df


def fill_postdate_from_pubdate(
    df: pd.DataFrame,
    source_col: str = "source",
    post_col: str = "postdate",
    pub_col: str = "pubDate",
) -> pd.DataFrame:
    df = ensure_string_col(df, post_col)
    if source_col not in df.columns or pub_col not in df.columns:
        return df
    is_news = df[source_col].astype(str).str.lower().eq("news")
    need_fill = is_news & (
        df[post_col].isna() | (df[post_col].astype(str).str.strip() == "")
    )
    if need_fill.any():
        df.loc[need_fill, post_col] = df.loc[need_fill, pub_col].map(to_yyyymmdd_str)
    return sanitize_postdate(df, post_col)


def ensure_is_posted_int(df: pd.DataFrame) -> pd.DataFrame:
    if "is_posted" not in df.columns:
        df["is_posted"] = 0
    df["is_posted"] = (
        pd.to_numeric(df["is_posted"], errors="coerce").fillna(0).astype(int)
    )
    return df


def merge_and_dedupe(
    existing: pd.DataFrame | None,
    new_items: list[dict],
    source: str,
    prioritize_posted: bool = True,
) -> pd.DataFrame:
    existing = existing if isinstance(existing, pd.DataFrame) else pd.DataFrame()
    new_df = pd.DataFrame(new_items).assign(source=source, is_posted=0)
    df = pd.concat([existing, new_df], ignore_index=True)
    df = ensure_is_posted_int(df)
    # is_posted=1 우선 보존(벨트+서스펜더)
    if prioritize_posted and "link" in df.columns:
        df = df.sort_values("is_posted", ascending=False).drop_duplicates(
            subset=["link"], keep="first"
        )
    else:
        df = df.drop_duplicates(subset=["link"])
    return df


def filter_last_n_days_postdate(
    df: pd.DataFrame, days: int = 7, post_col: str = "postdate"
) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if post_col not in df.columns:
        return pd.DataFrame(columns=df.columns)
    s = df[post_col].astype(str).str.strip().str.replace(r"\D", "", regex=True)
    dt = pd.to_datetime(s, format="%Y%m%d", errors="coerce")
    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
    mask = dt.notna() & (dt >= cutoff)
    return df.loc[mask].copy()
