import os
from datetime import datetime
from time import sleep
from typing import Literal

import pandas as pd
from tqdm import tqdm

from batch.fetch import fetch_data
from batch.product.keywords import (
    CREDIT_CARD_KEYWORDS,
    DEBIT_CARD_KEYWORDS,
    JADE_CARD_FEEDBACK_KEYWORDS,
    WONDER_CARD_FEEDBACK_KEYWORDS,
)
from batch.product.select_column import SOURCES_SELECT_MAP
from batch.utils import read_csv
from batch.variables import PRODUCT_SAVE_PATH
from logger import logger

FILE_TAG_QUERIES_MAP = {
    "credit": CREDIT_CARD_KEYWORDS,
    "debit": DEBIT_CARD_KEYWORDS,
    "wonder": JADE_CARD_FEEDBACK_KEYWORDS,
    "jade": WONDER_CARD_FEEDBACK_KEYWORDS,
}


def load_competitor_issues(
    file_tag: Literal["credit", "debit"],
) -> None:
    """경쟁사 신상품: 뉴스만 수집"""
    os.makedirs(PRODUCT_SAVE_PATH, exist_ok=True)
    file_path = os.path.join(PRODUCT_SAVE_PATH, f"news_{file_tag}.csv")
    existing_data = read_csv(file_path)
    items: list[dict[str, str]] = []
    for keyword in tqdm(FILE_TAG_QUERIES_MAP[file_tag], desc="news", leave=False):
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
        os.path.join(PRODUCT_SAVE_PATH, f"{file_tag}.csv"),
        index=False,
        encoding="utf-8",
    )
    logger.info(f"{file_path} scrap completed")


def load_ourproduct_issues(
    file_tag: Literal["wonder", "jade"],
) -> None:
    """자사 원더/JADE: 뉴스+블로그 수집"""
    os.makedirs(PRODUCT_SAVE_PATH, exist_ok=True)
    file_name = os.path.join(PRODUCT_SAVE_PATH, f"{file_tag}.csv")
    _df_list: list[pd.DataFrame] = [read_csv(file_name)]

    for source in ["news", "blog"]:
        file_path = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{file_tag}.csv")

        existing_data = read_csv(file_path)
        items: list[dict[str, str]] = []

        for keyword in tqdm(FILE_TAG_QUERIES_MAP[file_tag], desc=source, leave=False):
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
