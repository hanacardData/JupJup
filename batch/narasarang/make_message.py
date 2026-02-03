import re
from datetime import datetime, timedelta
from typing import Any

from batch.dml import fetch_df, mark_posted
from batch.fetch import fetch_trend_data
from batch.narasarang.gpt_rank import (
    dedup_title_url,
    filter_recent_days,
    gpt_rank_sorted,
)
from batch.narasarang.keywords import (
    COMPARE_ARMY_KEYWORDS,
)
from batch.narasarang.prompt import PROMPT, TEXT_INPUT
from bot.services.core.openai_client import async_openai_response
from logger import logger

TABLE = "narasarang"


def _get_title_keywords_for_brand(brand: str) -> list[str]:
    group = "하나카드" if brand == "hana" else "신한카드" if brand == "shinhan" else ""

    for g in COMPARE_ARMY_KEYWORDS:
        if g.get("groupName") == group:
            keywords = g.get("keywords", [])
            return [str(x).strip() for x in keywords if str(x).strip()]

    return []


def _title_has_any_keyword(title: str, keywords: list[str]) -> bool:
    t = (title or "").strip()
    if not t:
        return False

    t_nospace = re.sub(r"\s+", "", t)

    for k in keywords:
        if not k:
            continue
        k_stripped = k.strip()
        if not k_stripped:
            continue

        if k_stripped in t:
            return True

        k_nospace = re.sub(r"\s+", "", k_stripped)
        if k_nospace and k_nospace in t_nospace:
            return True

    return False


def _to_carousel_messages(picked: list[dict[str, Any]]) -> list[list[str]]:
    msgs: list[str] = []
    for it in picked:
        title = it.get("title", "").strip()
        summary = it.get("summary", "").strip()
        url = it.get("url", "").strip()
        if not (title and summary and url):
            continue
        msgs.append(f"제목: {title}\n내용: {summary}\n링크: {url}")

    return [
        msgs[i : i + 10]  # 10: 캐러셀 사이즈 제약
        for i in range(0, len(msgs), 10)
    ]


def _extract_urls(picked: list[dict[str, Any]]) -> list[str]:
    urls = []
    seen = set()
    for it in picked:
        u = it.get("url", "").strip()
        if u and u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def _load_brand_rows(brand: str) -> list[dict[str, Any]]:
    df = fetch_df(
        TABLE,
        cols=[
            "brand",
            "title",
            "url",
            "description",
            "post_date",
            "source",
            "is_posted",
        ],
    )
    if df.empty:
        return []

    sub = df.loc[df["brand"] == brand].copy()
    if sub.empty:
        return []

    return sub.to_dict(orient="records")


async def _make_brand_messages(
    brand: str,
    recent_days: int = 7,
    concurrency: int = 5,
) -> list[list[str]]:
    rows = _load_brand_rows(brand)
    if not rows:
        logger.info(f"[narasarang] no rows in db for brand={brand}")
        return []

    rows = filter_recent_days(rows, days=recent_days)
    rows = dedup_title_url(rows)

    before = len(rows)
    keywords = _get_title_keywords_for_brand(brand)
    rows = [r for r in rows if _title_has_any_keyword(r.get("title", ""), keywords)]
    logger.info(
        f"[narasarang] title keyword filter: brand={brand}, before={before}, after={len(rows)}"
    )

    logger.info(
        f"[narasarang] recent candidates: brand={brand}, days={recent_days}, n={len(rows)}"
    )
    if not rows:
        return []

    ranked = await gpt_rank_sorted(rows, concurrency=concurrency)

    logger.info(
        f"[narasarang] recent candidates: brand={brand}, days={recent_days}, n={len(rows)}"
    )
    if not rows:
        return []

    ranked = await gpt_rank_sorted(rows, concurrency=concurrency)
    logger.info(f"[narasarang] ranked(before filter): brand={brand}, n={len(ranked)}")

    ranked = [x for x in ranked if float(x.get("gpt_score", 0.0)) > 0.0]
    logger.info(
        f"[narasarang] ranked(after filter score>0): brand={brand}, n={len(ranked)}"
    )
    if not ranked:
        return []

    carousels = _to_carousel_messages(ranked)

    urls = _extract_urls(ranked)
    if urls:
        mark_posted(TABLE, urls)
        logger.info(f"[narasarang] mark_posted: brand={brand}, n={len(urls)}")

    return carousels


async def get_hana_narasarang_messages() -> list[list[str]]:
    return await _make_brand_messages(brand="hana", recent_days=3, concurrency=5)


async def get_shinhan_narasarang_messages() -> list[list[str]]:
    return await _make_brand_messages(brand="shinhan", recent_days=3, concurrency=5)


async def _get_trend_message() -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    one_week_ago = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    trend_response = fetch_trend_data(
        startDate=one_week_ago,
        endDate=today,
        timeUnit="date",
        keywordGroups=COMPARE_ARMY_KEYWORDS,
    )
    return await async_openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(content=trend_response.to_results()),
    )


async def get_trend_narasarng_messages() -> list[str]:
    trend_message = await _get_trend_message()
    message = [
        "💌 나라사랑카드 검색어 트렌드를 정리해드릴게요! ",
        trend_message,
    ]
    return message
