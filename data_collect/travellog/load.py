import os
from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from data_collect.fetch import fetch_data
from data_collect.travellog.keywords import TRAVELLOG_QUERIES
from data_collect.travellog.select_column import SOURCES_SELECT_MAP
from data_collect.utils import read_csv
from data_collect.variables import SAVE_PATH, SOURCES, TRAVELLOG_DATA_PATH
from logger import logger


def collect_load_travellog_data(queries: list[str]) -> None:
    """데이터를 수집하고 저장."""
    os.makedirs(SAVE_PATH, exist_ok=True)

    _df_list: list[pd.DataFrame] = [read_csv(TRAVELLOG_DATA_PATH)]
    for source in tqdm(SOURCES, disable=True):
        logger.info(f"{source} scrap started")
        _file_path = os.path.join(SAVE_PATH, f"_{source}_travellog.csv")
        _data_source = read_csv(_file_path)

        items: list[dict[str, str]] = []
        for keyword in tqdm(queries, disable=True):
            _data = fetch_data(
                type=source,
                query=keyword,
                sort="date",
            )
            sleep(0.05)
            if _data is None:
                logger.error(f"Failed to fetch data for {keyword} from {source}")
                continue
            _items = _data.to_items(
                query=keyword,
                scrap_date=datetime.today().strftime("%Y%m%d"),
            )
            items.extend(_items)

        _data_source = pd.concat(
            [_data_source, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        )
        _data_source = _data_source.drop_duplicates(subset=["link"])
        _data_source.to_csv(_file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_SELECT_MAP[source](_data_source))
        logger.info(f"{source} scrap completed")

    data = (
        pd.concat(_df_list, ignore_index=True)
        .sort_values(
            by=["is_posted", "scrap_date"], ascending=[False, True]
        )  # is_posted가 1인 경우, scrap_date 가 오래된 것을 남김
        .drop_duplicates(subset="link", keep="first")  # link 기준으로 중복 제거
    )
    data["scrap_date"] = data["scrap_date"].astype(str)
    data["post_date"] = data["post_date"].astype(str)
    data.to_csv(TRAVELLOG_DATA_PATH, index=False, encoding="utf-8")


if __name__ == "__main__":
    collect_load_travellog_data(TRAVELLOG_QUERIES)
