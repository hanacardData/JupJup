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

FILE_TAG_QUERIES_MAP: dict[str, list[str]] = {
    "credit": CREDIT_CARD_KEYWORDS,
    "debit": DEBIT_CARD_KEYWORDS,
    "wonder": JADE_CARD_FEEDBACK_KEYWORDS,
    "jade": WONDER_CARD_FEEDBACK_KEYWORDS,
}

FILE_TAG_SOURCES_MAP: dict[str, list[str]] = {
    "credit": ["news"],
    "debit": ["news"],
    "wonder": ["news", "blog"],
    "jade": ["news", "blog"],
}


def collect_load_product_issues(
    file_tag: Literal["credit", "debit", "wonder", "jade"],
) -> None:
    """
    경쟁사(credit/debit) 또는 자사(wonder/jade) 상품 이슈 데이터를 로드하고 처리합니다.
    - credit/debit: news 소스만 사용
    - wonder/jade: news 및 blog 소스 모두 사용
    """
    os.makedirs(PRODUCT_SAVE_PATH, exist_ok=True)

    final_file_name = os.path.join(PRODUCT_SAVE_PATH, f"{file_tag}.csv")

    _df_list: list[pd.DataFrame] = [read_csv(final_file_name)]
    sources_to_fetch = FILE_TAG_SOURCES_MAP[file_tag]
    for source in sources_to_fetch:
        source_file_path = os.path.join(PRODUCT_SAVE_PATH, f"{source}_{file_tag}.csv")
        existing_data = read_csv(source_file_path)
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

        df_new = pd.DataFrame(items).assign(source=source, is_posted=0)
        df = pd.concat(
            [existing_data, df_new],
            ignore_index=True,
        ).drop_duplicates(subset=["link"])
        df.to_csv(source_file_path, index=False, encoding="utf-8")
        _df_list.append(SOURCES_SELECT_MAP[source](df))

    data = (
        pd.concat(_df_list, ignore_index=True)
        .sort_values(
            by=["is_posted", "scrap_date"], ascending=[False, True]
        )  # is_posted가 1인 경우, scrap_date 가 오래된 것을 남김
        .drop_duplicates(subset="link", keep="first")  # link 기준으로 중복 제거
    )

    data.to_csv(final_file_name, index=False, encoding="utf-8")
    logger.info(f"{final_file_name} scrap completed")
