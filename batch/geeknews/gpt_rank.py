# batch/geeknews/gpt_rank.py
from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass

from batch.geeknews.rank import DB_PATH, GeekRow
from bot.services.core.openai_client import (  # 네 함수 위치에 맞게 import 수정
    async_openai_response,
)
from logger import logger


@dataclass
class GPTScored:
    row: GeekRow
    score: float


SCORING_PROMPT = """
당신은 하나카드의 업무에 도움되는 기술뉴스 큐레이터입니다.
아래 기사/글이 업무에 얼마나 유의미한지 0~100 점수로 평가하시오.

평가 기준:
- 금융/결제/핀테크/보안/개인정보 등 카드사 및 금융권 관련 정보: 중요도 1순위
- 업무 자동화 / 생산성 / 개발툴(DevOps, 워크플로, 자동화, API 등): 중요도 2순위
- AI/LLM 활용(에이전트, RAG, 프롬프트, 인퍼런스 등): 중요도 3순위
- 카카오, 토스 등 한국의 빅테크 회사 관련 이슈: 중요도 4순위

출력 형식:
- 반드시 숫자 하나만 출력 (예: 73)
- 다른 설명/문장/기호 출력 금지
""".strip()


def _make_input(row: GeekRow) -> str:
    content = (row.content or "").strip()
    if len(content) > 1500:
        content = content[:1500] + "..."

    return f"""[제목]
{row.title}

[내용]
{content}

[링크]
{row.url}
""".strip()


def _parse_score(text: str) -> float:
    """
    혹시라도 '73점' 같은 게 오면 숫자만 뽑아냄
    """
    if not text:
        return 0.0
    t = text.strip()

    try:
        v = float(t)
        return max(0.0, min(100.0, v))
    except Exception:
        pass

    digits = "".join(ch for ch in t if (ch.isdigit() or ch == "."))
    try:
        v = float(digits)
        return max(0.0, min(100.0, v))
    except Exception:
        return 0.0


async def score_one_with_gpt(row: GeekRow, semaphore: asyncio.Semaphore) -> float:
    async with semaphore:
        try:
            out = await async_openai_response(
                prompt=SCORING_PROMPT,
                input=_make_input(row),
            )
            return _parse_score(out)
        except Exception as e:
            logger.warning(f"[GeekNews] GPT scoring failed (id={row.id}): {e}")
            return 0.0


async def gpt_rerank(
    rows: list[GeekRow],
    top_k: int = 10,
    concurrency: int = 5,
) -> list[GeekRow]:
    """
    rows: 1차 규칙 점수로 줄여놓은 후보 리스트(예: 20개)
    top_k: 최종 몇 개만 반환할지
    concurrency: OpenAI 동시 호출 수 제한
    """
    if not rows:
        return []

    sem = asyncio.Semaphore(concurrency)
    scores = await asyncio.gather(
        *[score_one_with_gpt(r, sem) for r in rows],
        return_exceptions=True,
    )

    scored: list[GPTScored] = []
    for r, s in zip(rows, scores):
        if isinstance(s, Exception):
            logger.warning(f"[GeekNews] GPT score exception: {s}")
            continue
        scored.append(GPTScored(row=r, score=float(s)))

    scored.sort(key=lambda x: x.score, reverse=True)
    return [x.row for x in scored[:top_k]]


def update_gpt_scores(scored: list[tuple[int, float]]) -> None:
    if not scored:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            UPDATE geeknews
            SET gpt_score = ?, scored_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            [(float(score), int(id_)) for id_, score in scored],
        )
        conn.commit()


async def gpt_score_and_update(
    rows: list[GeekRow],
    concurrency: int = 5,
) -> list[tuple[int, float]]:
    """
    rows를 GPT로 스코어링하고, DB geeknews.gpt_score에 저장한다.
    return: [(id, gpt_score), ...]
    """
    if not rows:
        return []

    sem = asyncio.Semaphore(concurrency)

    async def _run(row: GeekRow) -> tuple[int, float]:
        score = await score_one_with_gpt(row, sem)
        return row.id, float(score)

    results = await asyncio.gather(*[_run(r) for r in rows], return_exceptions=True)

    cleaned: list[tuple[int, float]] = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"[GeekNews] GPT scoring exception: {r}")
            continue
        cleaned.append((int(r[0]), float(r[1])))

    update_gpt_scores(cleaned)
    logger.info(f"[GeekNews] Updated gpt_score rows={len(cleaned)}")
    return cleaned
