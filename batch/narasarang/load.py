from datetime import datetime

from batch.dml import insert_rows
from batch.fetch import fetch_data
from logger import logger

TABLE = "narasarang"


def _normalize_items(
    items: list[dict], brand: str, source_type: str, query: str
) -> list[dict]:
    rows = []
    for it in items:
        rows.append(
            {
                "brand": brand,
                "query": query,
                "title": it.get("title", ""),
                "url": it.get("link", ""),
                "description": it.get("description", ""),
                "post_date": it.get("postdate", "") or it.get("pubDate", ""),
                "scrap_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": source_type,
                "name": "",
                "is_posted": 0,
            }
        )
    return rows


def collect_load_narasarang_data(
    queries_by_brand: dict[str, list[str]], display: int = 30
) -> None:
    all_rows: list[dict] = []

    for brand, queries in queries_by_brand.items():
        for q in queries:
            for t in ("blog", "news", "cafe"):
                resp = fetch_data(
                    type=t, query=q, display=display, start=1, sort="date"
                )
                if not resp:
                    continue

                try:
                    items = [
                        x.model_dump() if hasattr(x, "model_dump") else dict(x)
                        for x in resp.items
                    ]
                except Exception:
                    try:
                        items = list(resp.items)
                    except Exception:
                        items = []

                all_rows.extend(
                    _normalize_items(items, brand=brand, source_type=t, query=q)
                )

    insert_rows(TABLE, all_rows)
    logger.info(f"Narasarang Data Collection Completed: rows={len(all_rows)}")
