import os
from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from batch.fetch import fetch_data
from batch.product.select_column import SOURCES_SELECT_MAP
from batch.utils import read_csv
from logger import logger


def _collect_data_common(queries: list[str], save_path: str, result_path: str) -> None:
    """데이터를 수집하고 저장."""
    os.makedirs(save_path, exist_ok=True)
    _df_list: list[pd.DataFrame] = [read_csv(result_path)]

    for source in tqdm(["news", "blog"], desc="source"):
        _file_path = os.path.join(save_path, f"_{source}_product.csv")
        _data_source = read_csv(_file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, disable=True):
            _data = fetch_data(
                type=source,
                query=keyword,
                sort="sim",
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
        logger.info(f"{_file_path} scrap completed")

    data = (
        pd.concat(_df_list, ignore_index=True)
        .sort_values(by=["is_posted", "scrap_date"], ascending=[False, True])
        .drop_duplicates(subset="link", keep="first")
    )
    data.to_csv(result_path, index=False, encoding="utf-8")
