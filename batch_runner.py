import asyncio
import json
import os
from datetime import datetime
from typing import Any

import pandas as pd
from holidayskr import is_holiday

from batch.app_review.android import get_app_reviews
from batch.compare_travel.make_message import get_compare_travel_message
from batch.database import init_database
from batch.dml import fetch_df
from batch.geeknews.load import collect_load_geeknews
from batch.geeknews.make_message import get_geeknews_message
from batch.issue.keywords import QUERIES
from batch.issue.load import collect_load_data
from batch.issue.make_message import get_issue_message
from batch.narasarang.keywords import NARASARANG_QUERIES
from batch.narasarang.load import collect_load_narasarang_data
from batch.narasarang.make_message import (
    get_hana_narasarang_messages,
    get_shinhan_narasarang_messages,
    get_trend_narasarng_messages,
)
from batch.product.load import collect_load_product_issues
from batch.product.make_message import process_generate_message
from batch.security_monitor.keywords import SECURITY_QUERIES
from batch.security_monitor.load import collect_load_security_issues
from batch.security_monitor.make_message import get_security_messages
from batch.travellog.keywords import TRAVELLOG_QUERIES
from batch.travellog.load import collect_load_travellog_data
from batch.travellog.make_message import get_travellog_message
from batch.variables import (
    DATA_PATH,
    NARASARANG_CHANNEL_ID,
    PRODUCT_CHANNEL_ID,
    SECURITY_CHANNEL_ID,
    SUBSCRIBE_CHANNEL_IDS,
    TEST_CHANNEL_ID,
    TRAVELLOG_CHANNEL_ID,
)
from bot.enums.button_templates import JUPJUP_BUTTON, PRODUCT_BUTTON
from bot.handler.message.channel import (
    handle_narasarang_command,
    handle_security_command,
)
from bot.services.batch_message.get_message import get_batch_message
from bot.services.core.post_payload import (
    async_post_message,
    async_post_payload,
)
from logger import logger


def is_skip_batch(date: datetime) -> bool:
    return is_holiday(date.strftime("%Y-%m-%d")) or date.weekday() >= 5


def data_collect():
    collect_load_data(QUERIES)
    logger.info("Issue Data Collection Completed")

    collect_load_travellog_data(TRAVELLOG_QUERIES)
    logger.info("Travellog Data Collection Completed")

    collect_load_security_issues(SECURITY_QUERIES)
    logger.info("Security Data Collection Completed")

    for file_tag in ["credit", "debit", "wonder", "jade"]:
        collect_load_product_issues(file_tag=file_tag)
    logger.info("Product Data Collection Completed")

    collect_load_geeknews()
    logger.info("Geeknews Collection Completed")

    collect_load_narasarang_data(NARASARANG_QUERIES)
    logger.info("Narasarang Collection Completed")


async def make_message(today_str: str, is_test: bool = False):
    try:  # Issue 메시지 생성
        logger.info("Generating issue message")
        issue_df = pd.read_csv(DATA_PATH, dtype={"post_date": object}, encoding="utf-8")
        issue_message = await get_issue_message(issue_df, tag=not is_test)
        logger.info("Created issue message")
    except Exception as e:
        logger.error(f"Failed to generate issue message: {e}")
        raise

    try:  # 트래블로그 메시지 생성
        logger.info("Generating travellog message")
        travellog_df = fetch_df("travellog")
        travellog_messages = await get_travellog_message(travellog_df, tag=not is_test)
        logger.info("Created travellog message")
    except Exception as e:
        logger.error(f"Failed to generate and send travellog message: {e}")
        raise

    try:  # Compare 트래블카드 메시지 생성
        travelcard_messages = await get_compare_travel_message()
        logger.info("Message ready: travelcard_messages")
    except Exception as e:
        logger.error(f"Failed to generate travelcard message: {e}")
        raise

    try:  # 보안 모니터링 메시지 생성
        logger.info("Generating security issue message")
        security_messages = await get_security_messages(tag=not is_test)
        logger.info("Created security issue messages")
    except Exception as e:
        logger.error(f"Failed to generate and send security alerts: {e}")
        raise

    try:  # 앱 리뷰 메시지 생성
        hanamoney_reviews, hanapay_reviews = get_app_reviews()
        logger.info("App review messages ready")
    except Exception as e:
        logger.error(f"Failed to send messag scrap app review: {e}")
        raise

    try:  # Geeknews 메시지 생성
        geeknews_messages = get_geeknews_message()
        logger.info("GeekNews messages ready")
    except Exception as e:
        logger.error(f"Failed to send messag scrap geeknews: {e}")
        raise

    try:  # 나라사랑카드 trend 메시지 생성
        trend_narasarang = await get_trend_narasarng_messages()
        hana_narasarang = await get_hana_narasarang_messages()
        shinhan_narasarang = await get_shinhan_narasarang_messages()
        narasarang_messages = {
            "trend": trend_narasarang,
            "hana": hana_narasarang,
            "shinhan": shinhan_narasarang,
        }
        logger.info(
            f"Narasarang messages ready: hana={len(hana_narasarang)}, shinhan={len(shinhan_narasarang)}"
        )
    except Exception as e:
        logger.error(f"Failed to generate narasarang messages: {e}")
        raise

    try:
        product_messages = {
            "/경쟁사신용": await process_generate_message("신용카드 신상품"),
            "/경쟁사체크": await process_generate_message("체크카드 신상품"),
            "/원더카드": await process_generate_message("원더카드 고객반응"),
            "/JADE": await process_generate_message("JADE 고객반응"),
        }
        logger.info("Created product messages")
    except Exception as e:
        logger.warning(f"Failed to generate product messages: {e}")
        raise

    ## 메세지 저장 로직
    try:
        output_dir = os.path.join("data", "messages")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"message_{today_str}.json")

        data: dict[str, Any] = {
            "issue": issue_message,
            "travellog": travellog_messages,
            "travelcard": travelcard_messages,
            "security": security_messages,
            "product": product_messages,
            "hanamoney": hanamoney_reviews,
            "hanapay": hanapay_reviews,
            "geeknews": geeknews_messages,
            "narasarang": narasarang_messages,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Message saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise


async def send_message(is_test: bool = False):
    try:
        await async_post_payload(JUPJUP_BUTTON, TEST_CHANNEL_ID)
        await async_post_payload(PRODUCT_BUTTON, TEST_CHANNEL_ID)
        if is_test:
            return

        # 트래블로그UX
        travellog_messages = get_batch_message("travellog")
        for message in [
            f"안녕하세요! 줍줍이입니다 🤗\n{datetime.today().strftime('%Y년 %m월 %d일')} 줍줍한 트래블로그 이슈를 공유드릴게요!\n"
        ] + travellog_messages:
            await async_post_message(message, TRAVELLOG_CHANNEL_ID)
            logger.info(f"Sent Travellog Message to channel {TRAVELLOG_CHANNEL_ID}")

        # 정보보안팀
        await handle_security_command(SECURITY_CHANNEL_ID)
        logger.info(f"Sent Message to channel {SECURITY_CHANNEL_ID}")

        # 나라사랑카드
        await handle_narasarang_command(NARASARANG_CHANNEL_ID)
        logger.info(f"Sent Narasarang Message to channel {NARASARANG_CHANNEL_ID}")

        await async_post_payload(PRODUCT_BUTTON, PRODUCT_CHANNEL_ID)
        for channel_id in SUBSCRIBE_CHANNEL_IDS:
            await async_post_payload(JUPJUP_BUTTON, channel_id)

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise


if __name__ == "__main__":
    logger.info("Batch started")
    init_database()  # db 초기화
    data_collect()  # 데이터 수집
    logger.info("Data collection completed")

    today_timestamp = datetime.now()
    if is_skip_batch(today_timestamp):
        logger.info(f"Not post today: {today_timestamp}")
    else:
        asyncio.run(
            make_message(today_str=today_timestamp.strftime("%Y-%m-%d"), is_test=False)
        )  # 메시지 생성
        logger.info("Message created")
        asyncio.run(send_message(is_test=False))  # 메시지 송신
        logger.info("Message sent")
    logger.info("Batch completed")
