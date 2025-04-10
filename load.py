import os
from time import sleep

import pandas as pd
from tqdm import tqdm

from fetch import fetch_data
from logger import logger
from refine import SOURCES_REFINE_MAP
from variables import DATA_PATH, QUERIES, SAVE_PATH, SOURCES


def _read_csv(file_path: str) -> pd.DataFrame:
    if os.path.exists(file_path):
        return pd.read_csv(file_path, encoding="utf-8")
    return pd.DataFrame()


def collect_load_data(queries: list[str]) -> None:
    """데이터를 수집하고 저장."""
    os.makedirs(SAVE_PATH, exist_ok=True)
    _df_list: list[pd.DataFrame] = [_read_csv(DATA_PATH)]
    for source in tqdm(SOURCES, desc="Souce"):
        logger.info(f"Collecting data from {source}")
        _file_path = os.path.join(SAVE_PATH, f"_{source}.csv")

        items: list[dict[str, str]] = []
        for keyword in tqdm(queries, desc="Keyword", leave=False):
            _data = fetch_data(
                type=source,
                query=keyword,
            )
            sleep(0.1)
            if _data is None:
                logger.error(f"Failed to fetch data for {keyword} from {source}")
                continue
            _items = _data.to_items()
            items.extend(_items)
        _data_source = _read_csv(_file_path)
        _data_source = pd.concat(
            [_data_source, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])
        _data_source.to_csv(_file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_REFINE_MAP[source](_data_source))
        logger.info(f"Completed Collecting data from {source}")

    data = pd.concat(_df_list, ignore_index=True).sort_values(
        by="is_posted", ascending=False
    )
    data_deduplicated = data.drop_duplicates(subset="link", keep="first")
    data_deduplicated.to_csv(DATA_PATH, index=False, encoding="utf-8")


if __name__ == "__main__":
    collect_load_data(QUERIES)
