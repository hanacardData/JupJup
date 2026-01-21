from datetime import datetime
from time import sleep

from tqdm import tqdm

from batch.dml import insert_rows
from batch.fetch import fetch_data
from batch.variables import SOURCES
from logger import logger


def collect_load_security_issues(queries: list[str]) -> None:
    for source in tqdm(["news"] + SOURCES, desc="source"):
        rows: list[dict] = []

        for keyword in tqdm(queries, desc=source, leave=False):
            result = fetch_data(source, keyword, display=100, sort="date")
            sleep(0.1)
            if result is None:
                logger.error(f"Failed to fetch data for {keyword} from {source}")
                continue

            items = result.to_items(
                query=keyword,
                scrap_date=datetime.today().strftime("%Y%m%d"),
            )

            for it in items:
                url = (it.get("link") or it.get("url") or "").strip()
                if not url:
                    continue

                rows.append(
                    {
                        "query": keyword,
                        "title": it.get("title", ""),
                        "url": url,
                        "description": it.get("description", ""),
                        "post_date": it.get("post_date", "")
                        or it.get("postdate", "")
                        or "",
                        "scrap_date": it.get(
                            "scrap_date", datetime.today().strftime("%Y%m%d")
                        ),
                        "source": source,
                        "name": it.get("name", "")
                        or it.get("bloggername", "")
                        or it.get("cafename", "")
                        or "",
                        "is_posted": 0,
                    }
                )

        insert_rows("security_monitor", rows)
        logger.info(f"security_monitor: inserted {len(rows)} rows (source={source})")
