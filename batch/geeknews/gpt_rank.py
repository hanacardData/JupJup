from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass

from bot.services.core.openai_client import async_openai_response
from logger import logger

DB_PATH = "jupjup.db"


@dataclass
class GeekRow:
    id: int
    title: str
    content: str
    url: str


SCORING_PROMPT = """
당신은 하나카드 관점의 '기술/이슈 뉴스' 우선순위 큐레이터입니다.
아래 기사/글이 하나카드 업무에 얼마나 중요한지 0~100 점수로 평가하세요.

[최우선: 크게 가산]
- 카드/결제/PG/지급결제, 금융권(은행/증권/보험) 인프라, 핀테크
- 보안사고, 해킹, 취약점, 악성코드, 침해사고 대응
- 개인정보/PII, 유출/노출, 인증/접근통제, 규제/컴플라이언스(예: 전자금융, 개인정보보호)
- 부정거래(Fraud), FDS, 계정탈취, 스미싱/피싱, 결제사기
- 각종 기술 및 정보의 누출 사례

[2순위: 국내(한국) 이슈]
- 한국 빅테크/플랫폼/금융사 관련 이슈(카카오/네이버/토스/카카오페이/카카오뱅크 등)
- 국내 규제/감독/사고/장애/분쟁 이슈

[3순위: 참고 가치]
- AI/LLM/RAG/에이전트 등 (단, 금융/보안/결제와 직접 연결되면 2순위 수준으로 상향)

[후순위: 낮게]
- 업무 자동화/생산성/개발툴(DevOps, 워크플로, 파이프라인, API, CLI 등)
- 데이터/SQL/ML 일반론 (금융/보안/결제와 무관하면 낮게)

[점수 가이드]
- 90~100: 카드/결제/금융 + 보안/개인정보/사기 이슈로 실무 임팩트 큼
- 70~89: 금융/보안/국내 이슈로 참고 가치 높음
- 40~69: 간접 관련/기술 트렌드 참고
- 0~39: 관련성 낮음

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


def fetch_candidates_for_gpt(limit: int = 30) -> list[GeekRow]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, content, url
            FROM geeknews
            WHERE is_posted = 0
              AND rule_score IS NOT NULL
              AND gpt_score IS NULL
            ORDER BY rule_score DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        GeekRow(
            id=int(r["id"]),
            title=str(r["title"]),
            content=str(r["content"]),
            url=str(r["url"]),
        )
        for r in rows
    ]


def update_gpt_scores(ids_scores: list[tuple[int, float]]) -> None:
    if not ids_scores:
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            UPDATE geeknews
            SET gpt_score = ?, scored_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            [(float(score), int(id_)) for id_, score in ids_scores],
        )
        conn.commit()


async def gpt_score_for_send(
    candidates: list[GeekRow],
    top_k: int = 10,
    concurrency: int = 5,
) -> list[tuple[int, float]]:
    if not candidates:
        return []

    sem = asyncio.Semaphore(concurrency)
    scores = await asyncio.gather(*[score_one_with_gpt(r, sem) for r in candidates])

    scored = [(r.id, float(s)) for r, s in zip(candidates, scores)]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[:top_k]
    update_gpt_scores(top)
    logger.info(f"[GeekNews] Stored gpt_score only for send: {len(top)} rows")
    return top
