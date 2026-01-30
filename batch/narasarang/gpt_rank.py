from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from bot.services.core.openai_client import async_openai_response
from logger import logger

KST = timezone(timedelta(hours=9))

SCORING_PROMPT = """
너는 카드 이슈 모니터링 담당자다.
입력 문서(나라사랑카드 관련 글/기사)를 읽고, '중요도'를 0~100 점수로 평가하고 1~2문장 요약을 만들어라.

[핵심 규칙: 브랜드 관련도 우선 반영]
- 점수(score)는 {brand} 브랜드 직접 관련도"를 종합 반영한 값이어야 한다.
- {brand} 나라사랑카드와 직접 관련될수록 점수를 적극적으로 높게 부여하라.
- {brand}가 중심이 아닌 타 카드사 중심 글, 단순 언급 수준의 비교글은 점수를 낮게 유지하라.

브랜드 관련도 판단 기준(가중치 높은 순):
1) 제목에 {brand} / {brand}카드 / {brand} 나라사랑카드 등이 직접 등장하면 매우 높은 가산점
2) 본문에서 {brand} 나라사랑카드 혜택/발급/후기/불만/조건변경을 구체적으로 다루면 높은 가산점
3) 여러 카드사를 비교하더라도 {brand}가 중심 주제이면 가산점
4) {brand}가 거의 등장하지 않거나 타 카드사가 중심이면 가산점 최소화

중요도 판단 기준(가중치 높은 순):
1) 실제 사용자 후기/경험(발급, 혜택 체감, 불만, 비교)
2) 정책/혜택/조건 변경, 이벤트/프로모션, 발급/전환/제한 이슈
3) 이슈성이 강한 내용(민원, 오류, 장애, 논란)
4) 중복/비슷한 글은 낮게(정보량 적으면 더 낮게)

출력 규칙(중요):
- 반드시 JSON 한 줄만 출력
- 코드펜스( ``` ) 절대 금지
- keys: score, summary
- summary는 존댓말로 요약
- 예: {"score":73,"summary":"OO카드의 발급 조건 변경에 대한 부정적 의견 및 PX 할인 체감 관련 긍정적 후기가 다수 언급되었습니다."}
""".strip()


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def _parse_post_date_to_dt(post_date: str) -> datetime | None:
    if not post_date:
        return None
    s = str(post_date).strip()

    if re.fullmatch(r"\d{8}", s):
        try:
            dt = datetime.strptime(s, "%Y%m%d")
            return dt.replace(tzinfo=KST)
        except Exception:
            return None

    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
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
    items: list[dict[str, Any]],
    days: int = 3,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    now = now or datetime.now(tz=KST)
    cutoff = now - timedelta(days=days)

    out: list[dict[str, Any]] = []
    for it in items:
        pd = (it.get("post_date") or "").strip()
        dt = _parse_post_date_to_dt(pd)
        if dt is None:
            continue
        if dt >= cutoff:
            it2 = dict(it)
            it2["_post_dt"] = dt
            out.append(it2)

    out.sort(key=lambda x: x.get("_post_dt"), reverse=True)
    return out


def dedup_title_url(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        title = (it.get("title") or "").strip()
        url = (it.get("url") or "").strip()
        key = (title, url)
        if not title or not url:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _make_input(it: dict[str, Any]) -> str:
    brand = (it.get("brand") or "").strip()
    title = _strip_html((it.get("title") or "").strip())
    desc = _strip_html((it.get("description") or "").strip())
    url = (it.get("url") or "").strip()
    post_date = (it.get("post_date") or "").strip()
    source = (it.get("source") or "").strip()

    if len(desc) > 1500:
        desc = desc[:1500] + "..."

    return f"""[브랜드]
{brand}

[제목]
{title}

[내용]
{desc}

[링크]
{url}

[작성일]
{post_date}

[출처]
{source}
""".strip()


def _safe_json_obj(raw: str) -> dict:
    if not raw:
        raise ValueError("empty response")

    s = raw.strip()

    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s).strip()

    left = s.find("{")
    right = s.rfind("}")
    if left == -1 or right == -1 or right <= left:
        raise ValueError(f"no json object: {s[:200]}")
    return json.loads(s[left : right + 1])


def _parse_score_summary(raw: str) -> tuple[float, str]:
    try:
        obj = _safe_json_obj(raw)
        score = float(obj.get("score", 0.0))
        score = max(0.0, min(100.0, score))
        summary = str(obj.get("summary", "")).strip()
        if len(summary) > 180:
            summary = summary[:180] + "..."
        return score, summary
    except Exception:
        return 0.0, ""


async def _score_one(it: dict[str, Any], sem: asyncio.Semaphore) -> tuple[float, str]:
    async with sem:
        try:
            brand = (it.get("brand") or "").strip()
            prompt = SCORING_PROMPT.replace("{brand}", brand)

            raw = await async_openai_response(
                prompt=prompt,
                input=_make_input(it),
            )
            return _parse_score_summary(raw)
        except Exception as e:
            logger.warning(f"[narasarang] gpt scoring failed url={it.get('url')}: {e}")
            return 0.0, ""


async def gpt_rank_topk(
    items: list[dict[str, Any]],
    top_k: int = 10,
    concurrency: int = 5,
) -> list[dict[str, Any]]:
    if not items:
        return []

    sem = asyncio.Semaphore(concurrency)
    scored = await asyncio.gather(*[_score_one(it, sem) for it in items])

    merged: list[dict[str, Any]] = []
    for it, (score, summary) in zip(items, scored):
        it2 = dict(it)
        it2["gpt_score"] = float(score)
        it2["summary"] = summary
        merged.append(it2)

    merged.sort(key=lambda x: x.get("gpt_score", 0.0), reverse=True)
    merged = [x for x in merged if (x.get("summary") or "").strip()]
    return merged[:top_k]
