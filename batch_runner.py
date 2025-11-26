import asyncio
import json
import os
from datetime import datetime

import pandas as pd
from holidayskr import is_holiday

from batch.app_review.android import get_app_reviews
from batch.compare_travel.make_message import get_compare_travel_message
from batch.issue.keywords import QUERIES
from batch.issue.load import collect_load_data
from batch.issue.make_message import get_issue_message
from batch.product.load import collect_load_product_issues
from batch.product.make_message import load_and_make_message
from batch.security_monitor.keywords import SECURITY_QUERIES
from batch.security_monitor.load import collect_load_security_issues
from batch.security_monitor.make_message import get_security_messages
from batch.travellog.keywords import TRAVELLOG_QUERIES
from batch.travellog.load import collect_load_travellog_data
from batch.travellog.make_message import get_travellog_message
from batch.variables import (
    DATA_PATH,
    PRODUCT_CHANNEL_ID,
    SECURITY_CHANNEL_ID,
    SECURITY_DATA_PATH,
    SUBSCRIBE_CHANNEL_IDS,
    TEST_CHANNEL_ID,
    TRAVELLOG_CHANNEL_ID,
    TRAVELLOG_DATA_PATH,
)
from bot.enums.button_templates import JUPJUP_BUTTON, PRODUCT_BUTTON
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
        travellog_df = pd.read_csv(
            TRAVELLOG_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        travellog_messages = await get_travellog_message(travellog_df, tag=not is_test)
        logger.info("Created travellog message")

        # 트래블로그 부 메세지 송신
        if not is_test:
            for message in travellog_messages:
                await async_post_message(message, TRAVELLOG_CHANNEL_ID)
            logger.info(f"Sent Travellog Message to channel {TRAVELLOG_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to generate and send travellog message: {e}")
        await async_post_message(f"travellog error: {str(e)}", TEST_CHANNEL_ID)
        raise

    try:  # Compare 트래블카드 메시지 생성
        travelcard_messages = await get_compare_travel_message()
        logger.info("Message ready: travelcard_messages")
    except Exception as e:
        logger.error(f"Failed to generate travelcard message: {e}")
        raise

    try:  # 보안 모니터링 메시지 생성
        logger.info("Generating security issue message")
        security_df = pd.read_csv(
            SECURITY_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        security_messages = await get_security_messages(security_df, tag=not is_test)
        logger.info("Created security issue messages")
        for message in security_messages:
            await async_post_message(message, TEST_CHANNEL_ID)
        # 보안 모니터링 메세지 송신
        if not is_test:
            for message in security_messages:
                await async_post_message(message, SECURITY_CHANNEL_ID)
            logger.info(f"Sent Message to channel {SECURITY_CHANNEL_ID}")

    except Exception as e:
        logger.error(f"Failed to generate and send security alerts: {e}")
        await async_post_message(f"Security error: {str(e)}", TEST_CHANNEL_ID)
        raise

    try:  # 앱 리뷰 메시지 송신
        hanamoney_reviews, hanapay_reviews = get_app_reviews()
        logger.info("App review messages ready")
    except Exception as e:
        logger.error(f"Failed to send messag scrap app review: {e}")
        raise

    try:
        product_messages = {
            "/경쟁사신용": await load_and_make_message("신용카드 신상품"),
            "/경쟁사체크": await load_and_make_message("체크카드 신상품"),
            "/원더카드": await load_and_make_message("원더카드 고객반응"),
            "/JADE": await load_and_make_message("JADE 고객반응"),
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

        data: dict[str, list[str] | dict[str, list[str]]] = {
            "issue": issue_message,
            "travellog": travellog_messages,
            "travelcard": travelcard_messages,
            "security": security_messages,
            "product": product_messages,
            "hanamoney": hanamoney_reviews,
            "hanapay": hanapay_reviews,
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

        await async_post_payload(PRODUCT_BUTTON, PRODUCT_CHANNEL_ID)
        for channel_id in SUBSCRIBE_CHANNEL_IDS:
            await async_post_payload(JUPJUP_BUTTON, channel_id)

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise


if __name__ == "__main__":
    logger.info("Batch started")

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
