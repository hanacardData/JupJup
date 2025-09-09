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
    file_path = os.path.join(save_path, f"news_{file_tag}.csv")
    existing_data = read_csv(file_path)
    items: list[dict[str, str]] = []
    for keyword in tqdm(queries, desc="news", leave=False):
        result = fetch_data("news", keyword, display=100, sort="sim")
        sleep(0.1)
        if result is None:
            logger.error(f"Failed to fetch data for {keyword} from news")
            continue
        items.extend(
            result.to_items(
                query=keyword, scrap_date=datetime.today().strftime("%Y%m%d")
            )
        )

    df = (
        pd.concat(
            [existing_data, pd.DataFrame(items).assign(source="news", is_posted=0)],
            ignore_index=True,
        )
        .sort_values(
            by=["is_posted", "scrap_date"],
            ascending=[
                False,
                True,
            ],  # is_posted가 1인 경우, scrap_date 가 오래된 것을 남김
        )
        .drop_duplicates(subset="link", keep="first")  # link 기준으로 중복 제거
    )

    df.to_csv(file_path, index=False, encoding="utf-8")
    SOURCES_SELECT_MAP["news"](df).to_csv(
        os.path.join(save_path, f"{file_tag}.csv"), index=False, encoding="utf-8"
    )
    logger.info(f"{file_path} scrap completed")


def load_ourproduct_issues(
    queries: list[str],
    save_path: str,
    file_tag: str,
) -> None:
    """자사 원더/JADE: 뉴스+블로그 수집"""
    os.makedirs(save_path, exist_ok=True)
    file_name = os.path.join(save_path, f"{file_tag}.csv")
    _df_list: list[pd.DataFrame] = [read_csv(file_name)]

    for source in ["news", "blog"]:
        file_path = os.path.join(save_path, f"{source}_{file_tag}.csv")

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

    data = (
        pd.concat(_df_list, ignore_index=True)
        .sort_values(
            by=["is_posted", "scrap_date"], ascending=[False, True]
        )  # is_posted가 1인 경우, scrap_date 가 오래된 것을 남김
        .drop_duplicates(subset="link", keep="first")  # link 기준으로 중복 제거
    )
    data.to_csv(file_name, index=False, encoding="utf-8")
    logger.info(f"{file_name} scrap completed")
