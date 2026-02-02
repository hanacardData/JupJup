import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from batch.narasarang.prompt import SCORE_INPUT, SCORING_PROMPT
from bot.services.core.openai_client import async_openai_response
from logger import logger

KST = timezone(timedelta(hours=9))


def _parse_post_date_to_dt(post_date: str) -> datetime | None:
    if not post_date:
        return None
    s = str(post_date).strip()

    if re.fullmatch(r"\d{8}", s):
        try:
            return datetime.strptime(s, "%Y%m%d").replace(tzinfo=KST)
        except Exception:
            return

    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=KST)
        return dt.astimezone(KST)
    except Exception:
        pass

    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=KST)
        return dt.astimezone(KST)
    except Exception:
        return None


def filter_recent_days(
    items: list[dict[str, str | None]],
    days: int = 7,
    now: datetime | None = None,
) -> list[dict[str, str | None]]:
    now = now or datetime.now(tz=KST)
    cutoff = now - timedelta(days=days)

    out: list[dict[str, str | None]] = []
    for it in items:
        pd = it.get("post_date", "").strip()
        dt = _parse_post_date_to_dt(pd)
        if dt is None:
            continue
        if dt >= cutoff:
            it2 = dict(it)
            it2["_post_dt"] = dt
            out.append(it2)

    out.sort(key=lambda x: x.get("_post_dt"), reverse=True)
    return out


def dedup_title_url(items: list[dict[str, str | None]]) -> list[dict[str, str | None]]:
    seen = set()
    out = []
    for it in items:
        title = it.get("title", "").strip()
        url = it.get("url", "").strip()
        key = (title, url)
        if not title or not url:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _make_input(it: dict[str, str | None]) -> str:
    desc = it.get("description", "").strip()
    if len(desc) > 1500:
        desc = f"{desc[:1500]}..."

    return SCORE_INPUT.format(
        brand=it.get("brand", "").strip(),
        title=it.get("title", "").strip(),
        desc=desc,
        url=it.get("url", "").strip(),
        post_date=it.get("post_date", "").strip(),
        source=it.get("source", "").strip(),
    )


def _safe_json_obj(raw: str) -> dict:
    if not raw:
        raise ValueError("empty response")

    s = raw.strip()

    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s).strip()

    return json.loads(s)


def _parse_score_summary(raw: str) -> tuple[float, str]:
    try:
        obj = _safe_json_obj(raw)
        score = float(obj.get("score", 0.0))
        score = max(0.0, min(100.0, score))
        summary = str(obj.get("summary", "")).strip()
        if len(summary) > 180:
            summary = f"{summary[:180]}..."
        return score, summary
    except Exception:
        return 0.0, ""


async def _score_one(
    it: dict[str, str | None], sem: asyncio.Semaphore
) -> tuple[float, str]:
    async with sem:
        try:
            brand = it.get("brand", "").strip()
            prompt = SCORING_PROMPT.replace("{brand}", brand)

            raw = await async_openai_response(
                prompt=prompt,
                input=_make_input(it),
            )
            return _parse_score_summary(raw)
        except Exception as e:
            logger.warning(f"[narasarang] gpt scoring failed url={it.get('url')}: {e}")
            return 0.0, ""


async def gpt_rank_sorted(
    items: list[dict[str, str | None]],
    concurrency: int = 5,
) -> list[dict[str, str | None]]:
    if not items:
        return []

    sem = asyncio.Semaphore(concurrency)
    scored = await asyncio.gather(*[_score_one(it, sem) for it in items])

    merged: list[dict[str, str | None]] = []
    for it, (score, summary) in zip(items, scored):
        it2 = dict(it)
        it2["gpt_score"] = float(score)
        it2["summary"] = summary
        merged.append(it2)

    merged = [x for x in merged if x.get("summary", "").strip()]
    merged.sort(key=lambda x: x.get("gpt_score", 0.0), reverse=True)
    return merged
