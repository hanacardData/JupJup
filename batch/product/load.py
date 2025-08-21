import os
from datetime import datetime
from time import sleep

import pandas as pd
from tqdm import tqdm

from batch.fetch import fetch_data
from batch.product.select_column import SOURCES_SELECT_MAP
from batch.utils import read_csv
from logger import logger


def load_competitor_issues(
    queries: list[str],
    save_path: str,
    file_tag: str,
) -> None:
    """경쟁사 신상품: 뉴스만 수집"""
    os.makedirs(save_path, exist_ok=True)

    _df_list: list[pd.DataFrame] = []

    for source in ["news"]:
        file_name = f"{source}_{file_tag}.csv"
        file_path = os.path.join(save_path, file_name)

        existing_data = read_csv(file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, desc=source, leave=False):
            result = fetch_data(source, keyword, display=100, sort="sim")
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
            [existing_data, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])

        df.to_csv(file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_SELECT_MAP[source](df))
        logger.info(f"{file_path} scrap completed")


def load_ourproduct_issues(
    queries: list[str],
    save_path: str,
    file_tag: str,
) -> None:
    """자사 원더/JADE: 뉴스+블로그 수집"""
    os.makedirs(save_path, exist_ok=True)

    _df_list: list[pd.DataFrame] = []

    for source in ["news", "blog"]:
        file_name = f"{source}_{file_tag}.csv"
        file_path = os.path.join(save_path, file_name)

        existing_data = read_csv(file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(queries, desc=source, leave=False):
            result = fetch_data(source, keyword, display=100, sort="sim")
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
            [existing_data, pd.DataFrame(items).assign(source=source, is_posted=0)],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])

        df.to_csv(file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_SELECT_MAP[source](df))
        logger.info(f"{file_path} scrap completed")
