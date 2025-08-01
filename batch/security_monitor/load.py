import os
from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from batch.fetch import fetch_data
from batch.security_monitor.select_column import SOURCES_SELECT_MAP
from batch.utils import read_csv
from batch.variables import SECURITY_DATA_PATH, SECURITY_SAVE_PATH, SECURITY_SOURCES
from logger import logger


def load_security_issues(queries: list[str]) -> None:
    os.makedirs(SECURITY_SAVE_PATH, exist_ok=True)

    _df_list: list[pd.DataFrame] = [read_csv(SECURITY_DATA_PATH)]

    for source in tqdm(SECURITY_SOURCES, desc="source"):
        file_path = os.path.join(SECURITY_SAVE_PATH, f"{source}.csv")
        existing = read_csv(file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, desc=source, leave=False):
            result = fetch_data(source, keyword)
            sleep(0.1)
            if result is None:
                logger.error(f"Failed to fetch data for {keyword} from {source}")
                continue
            items.extend(
                result.to_items(
                    query=keyword, scrap_date=datetime.today().strftime("%Y%m%d")
                )
            )

        df = pd.concat(
            [existing, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])

        df.to_csv(file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_SELECT_MAP[source](df))
        logger.info(f"{file_path} scrap completed")

    final = (
        pd.concat(_df_list, ignore_index=True)
        .sort_values(by=["is_posted", "scrap_date"], ascending=[False, True])
        .drop_duplicates(subset="link", keep="first")
    )
    final.to_csv(SECURITY_DATA_PATH, index=False, encoding="utf-8")
