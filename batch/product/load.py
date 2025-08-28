import os
from datetime import datetime
from time import sleep

from tqdm import tqdm

from batch.fetch import fetch_data
from batch.product.common import (
    fill_postdate_from_pubdate,
    merge_and_dedupe,
)
from batch.utils import read_csv
from logger import logger


def _save_one(source: str, file_path: str, items: list[dict[str, str]]) -> None:
    existing = read_csv(file_path)
    df = merge_and_dedupe(existing, items, source=source, prioritize_posted=True)
    if source == "news":
        df = fill_postdate_from_pubdate(
            df, source_col="source", post_col="postdate", pub_col="pubDate"
        )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False, encoding="utf-8")
    logger.info(f"{file_path} scrap completed")


def load_competitor_issues(queries: list[str], save_path: str, file_tag: str) -> None:
    """경쟁사 신상품: 뉴스만 수집"""
    os.makedirs(save_path, exist_ok=True)
    for source in ["news"]:
        file_path = os.path.join(save_path, f"{source}_{file_tag}.csv")
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
        _save_one(source, file_path, items)


def load_ourproduct_issues(queries: list[str], save_path: str, file_tag: str) -> None:
    """자사 원더/JADE: 뉴스+블로그 수집"""
    os.makedirs(save_path, exist_ok=True)
    for source in ["news", "blog"]:
        file_path = os.path.join(save_path, f"{source}_{file_tag}.csv")
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
        _save_one(source, file_path, items)
