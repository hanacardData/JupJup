from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from batch.dml import insert_rows
from batch.fetch import fetch_data
from batch.travellog.select_column import SCHEMA, SOURCES_SELECT_MAP
from batch.variables import SOURCES
from logger import logger


def collect_load_travellog_data(queries: list[str]) -> None:
    """데이터를 수집하고 저장."""
    all_rows: list[dict[str, str]] = []

    for source in tqdm(SOURCES, disable=True):
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, disable=True):
            _data = fetch_data(
                type=source,
                query=keyword,
                sort="date",
                display=100,
            )
            sleep(0.05)
            if _data is None:
                logger.error(f"Failed to fetch data for {keyword} from {source}")
                continue
            _items = _data.to_items(
                query=keyword,
                scrap_date=datetime.today().strftime("%Y%m%d"),
            )
            for it in _items:
                it["source"] = source
                it["is_posted"] = 0
            items.extend(_items)

        if items:
            for it in items:
                it["url"] = it.get("link", "")
                it["scrap_date"] = str(
                    it.get("scrap_date", datetime.today().strftime("%Y%m%d"))
                )
            df = SOURCES_SELECT_MAP[source](pd.DataFrame(items))
        else:
            df = pd.DataFrame(columns=SCHEMA)

        all_rows.extend(df.to_dict(orient="records"))
        logger.info(f"issue scrap completed: source={source}, rows={len(df)}")

    insert_rows("travellog", all_rows)
