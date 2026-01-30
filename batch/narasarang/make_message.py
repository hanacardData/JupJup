from typing import Any

from batch.dml import fetch_df
from batch.narasarang.gpt_rank import (
    dedup_title_url,
    filter_recent_days,
    gpt_rank_topk,
)
from logger import logger

TABLE = "narasarang"


def _to_carousel_messages(picked: list[dict[str, Any]]) -> list[str]:
    msgs: list[str] = []
    for it in picked:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        url = (it.get("url") or "").strip()
        if not (title and summary and url):
            continue
        msgs.append(f"제목: {title}\n내용: {summary}\n링크: {url}")
    return msgs


def _load_brand_rows(brand: str) -> list[dict[str, Any]]:
    df = fetch_df(
        TABLE,
        cols=["brand", "title", "url", "description", "post_date", "source"],
    )
    if df.empty:
        return []

    sub = df[df["brand"] == brand].copy()
    if sub.empty:
        return []

    return sub.to_dict(orient="records")


async def _make_brand_messages(
    brand: str,
    top_k: int = 10,
    recent_days: int = 3,
    concurrency: int = 5,
) -> list[str]:
    rows = _load_brand_rows(brand)
    if not rows:
        logger.info(f"[narasarang] no rows in db for brand={brand}")
        return []

    rows = filter_recent_days(rows, days=recent_days)
    rows = dedup_title_url(rows)

    logger.info(
        f"[narasarang] recent candidates: brand={brand}, days={recent_days}, n={len(rows)}"
    )
    if not rows:
        return []

    picked = await gpt_rank_topk(rows, top_k=top_k, concurrency=concurrency)
    logger.info(f"[narasarang] picked: brand={brand}, n={len(picked)}")
    return _to_carousel_messages(picked)


async def get_hana_narasarang_messages(top_k: int = 10) -> list[str]:
    return await _make_brand_messages(
        brand="hana", top_k=top_k, recent_days=3, concurrency=5
    )


async def get_shinhan_narasarang_messages(top_k: int = 10) -> list[str]:
    return await _make_brand_messages(
        brand="shinhan", top_k=top_k, recent_days=3, concurrency=5
    )
