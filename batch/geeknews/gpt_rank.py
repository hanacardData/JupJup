import asyncio
import json
import re

from pydantic import BaseModel

from bot.services.core.openai_client import async_openai_response
from logger import logger


class GeekNewsItem(BaseModel):
    title: str
    url: str
    content: str
    rule_score: float
    gpt_score: float | None = None
    topic: str | None = None


SCORING_PROMPT = """
당신은 하나카드 관점의 '기술/이슈 뉴스' 우선순위 큐레이터입니다.
1. 아래 기사/글이 하나카드 업무에 얼마나 중요한지 0~100 점수로 평가하세요.
2. 아래 기사/글의 대주제를 공백 포함 8글자 이내의 한국어로 추출하세요.

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
- 반드시 JSON 한 줄로만 출력
- keys: score, topic
- score: 0~100 숫자
- topic: 뉴스의 대주제(공백 포함 8글자 이내)
- 예: {"score":73,"topic":"라우터 해킹"}
- 다른 문장/설명 출력 금지
""".strip()


def _make_prompt_input(row: GeekNewsItem) -> str:
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


def _parse_score_topic(text: str) -> tuple[float, str]:
    if not text:
        return 0.0, "기타"

    t = text.strip()

    try:
        obj = json.loads(t)
        score = float(obj.get("score", 0.0))
        topic = str(obj.get("topic", "")).strip()
        score = max(0.0, min(100.0, score))
        topic = topic if topic else "기타"
        topic = topic[:10]
        return score, topic
    except Exception:
        pass

    score = 0.0
    topic = "기타"

    m_score = re.search(r"(\d+(\.\d+)?)", t)
    if m_score:
        try:
            score = float(m_score.group(1))
            score = max(0.0, min(100.0, score))
        except Exception:
            score = 0.0

    m_topic = re.search(r"topic\"?\s*[:=]\s*\"?([^\"}\n]+)", t, re.IGNORECASE)
    if m_topic:
        topic = m_topic.group(1).strip() or "기타"

    return score, topic[:8]


async def _gpt_score_one_item(
    item: GeekNewsItem, semaphore: asyncio.Semaphore
) -> tuple[float, str]:
    async with semaphore:
        try:
            out = await async_openai_response(
                prompt=SCORING_PROMPT,
                input=_make_prompt_input(item),
            )
            return _parse_score_topic(out)
        except Exception as e:
            logger.warning(f"[GeekNews] GPT scoring failed (url={item.url}): {e}")
            return 0.0, "기타"


async def gpt_score_from_items(
    items: list[GeekNewsItem],
    concurrency: int = 5,
) -> list[tuple[float, str]]:
    if not items:
        return []
    sem = asyncio.Semaphore(concurrency)
    results = await asyncio.gather(*[_gpt_score_one_item(it, sem) for it in items])
    return [(float(s), str(tp)) for (s, tp) in results]
