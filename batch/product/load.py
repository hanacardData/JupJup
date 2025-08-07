import os
from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from batch.fetch import fetch_data
from batch.product.select_column import SOURCES_SELECT_MAP
from batch.utils import read_csv
from logger import logger


def _collect_data_common(
    queries: list[str],
    save_path: str,
    file_tag: str,
) -> None:
    os.makedirs(save_path, exist_ok=True)
    df_list: list[pd.DataFrame] = []

    for source in tqdm(["news", "blog"], desc="source"):
        file_name = f"{source}_{file_tag}.csv"
        file_path = os.path.join(save_path, file_name)

        existing_data = read_csv(file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, desc=source, leave=False):
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

        raw_df = pd.concat(
            [existing_data, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])

        selected_df = SOURCES_SELECT_MAP[source](raw_df)
        selected_df.to_csv(file_path, index=False, encoding="utf-8")

        df_list.append(selected_df)
        logger.info(f"{file_path} scrap completed")
