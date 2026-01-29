import json
import re

from batch.dml import fetch_df
from batch.narasarang.prompt import PROMPT, TEXT_INPUT
from bot.services.core.openai_client import async_openai_response
from logger import logger

TABLE = "narasarang"


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def _load_candidates(brand: str, limit: int = 50) -> list[dict]:
    df = fetch_df(
        TABLE, cols=["brand", "title", "url", "description", "post_date", "source"]
    )
    if df.empty:
        return []

    sub = df[df["brand"] == brand].copy()
    if sub.empty:
        return []

    sub["title"] = sub["title"].fillna("").apply(_strip_html)
    sub["description"] = sub["description"].fillna("").apply(_strip_html)
    sub["url"] = sub["url"].fillna("").astype(str).str.strip()

    sub = sub.drop_duplicates(subset=["title", "url"]).head(limit)

    out: list[dict] = []
    for _, r in sub.iterrows():
        title = (r.get("title") or "").strip()
        url = (r.get("url") or "").strip()
        if not title or not url:
            continue
        out.append(
            {
                "title": title[:140],
                "description": (r.get("description") or "")[:400],
                "url": url,
                "source": (r.get("source") or ""),
                "post_date": (r.get("post_date") or ""),
            }
        )
    return out


def _to_carousel_messages(picked: list[dict]) -> list[str]:
    msgs: list[str] = []
    for it in picked:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        url = (it.get("url") or "").strip()
        if not (title and summary and url):
            continue
        msgs.append(f"제목: {title}\n내용: {summary}\n링크: {url}")
    return msgs


async def _pick_topk_with_gpt(brand: str, top_k: int = 10) -> list[str]:
    candidates = _load_candidates(brand=brand, limit=max(50, top_k * 5))
    if not candidates:
        return []

    content = json.dumps(candidates, ensure_ascii=False, indent=2)

    raw = await async_openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(brand=brand, top_k=top_k, content=content),
    )

    try:
        data = json.loads(raw)
        picked = data.get("picked", [])
        if not isinstance(picked, list):
            return []
        return _to_carousel_messages(picked)[:top_k]
    except Exception as e:
        logger.error(
            f"[narasarang] failed to parse gpt json: {e} / raw={str(raw)[:300]}"
        )
        return []


async def get_hana_narasarang_messages(top_k: int = 10) -> list[str]:
    return await _pick_topk_with_gpt(brand="hana", top_k=top_k)


async def get_shinhan_narasarang_messages(top_k: int = 10) -> list[str]:
    return await _pick_topk_with_gpt(brand="shinhan", top_k=top_k)
