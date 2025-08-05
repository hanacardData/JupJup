import asyncio
import json
import os
from datetime import datetime

import pandas as pd
from holidayskr import is_holiday

from batch.compare_travel.make_message import get_compare_travel_message
from batch.issue.keywords import QUERIES
from batch.issue.load import collect_load_data
from batch.issue.make_message import get_issue_message
from batch.product.keywords import (
    CREDIT_CARD_KEYWORDS,
    DEBIT_CARD_KEYWORDS,
    JADE_CARD_FEEDBACK_KEYWORDS,
    WONDER_CARD_FEEDBACK_KEYWORDS,
)
from batch.product.make_message import get_product_message
from batch.security_monitor.keywords import SECURITY_QUERIES
from batch.security_monitor.load import load_security_issues
from batch.security_monitor.make_message import get_security_messages
from batch.travellog.keywords import TRAVELLOG_QUERIES
from batch.travellog.load import collect_load_travellog_data
from batch.travellog.make_message import get_travellog_message
from batch.variables import (
    DATA_PATH,
    PRODUCT_CHANNEL_ID,
    PRODUCT_DATA_PATH,
    SECURITY_CHANNEL_ID,
    SECURITY_DATA_PATH,
    SUBSCRIBE_CHANNEL_IDS,
    TEST_CHANNEL_ID,
    TRAVELLOG_CHANNEL_ID,
    TRAVELLOG_DATA_PATH,
)
from bot.enums.button_templates import JUPJUP_BUTTON, PRODUCT_BUTTON
from bot.services.core.post_button import async_post_button_to_channel
from bot.services.core.post_message import post_message_to_channel
from logger import logger


def is_skip_batch(date: datetime) -> bool:
    return is_holiday(date.strftime("%Y-%m-%d")) or date.weekday() >= 5


def data_collect():
    logger.info("Issue Data Collection Strarted")
    collect_load_data(QUERIES)
    logger.info("Issue Data Collection Completed")

    logger.info("Travellog Data Collection Started")
    collect_load_travellog_data(TRAVELLOG_QUERIES)
    logger.info("Travellog Data Collection Completed")

    logger.info("Security Data Collection Started")
    load_security_issues(SECURITY_QUERIES)
    logger.info("Security Data Collection Completed")


def make_message(is_test: bool = False):
    today_timestamp = datetime.now()
    if is_skip_batch(today_timestamp):
        logger.info(f"Not post today: {today_timestamp}")
        return

    try:  # Issue 메시지 생성
        logger.info("Generating issue message")
        issue_df = pd.read_csv(DATA_PATH, dtype={"post_date": object}, encoding="utf-8")
        issue_message = get_issue_message(issue_df, tag=not is_test)
        logger.info("Created issue message")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:  # 트래블로그 메시지 생성
        logger.info("Generating travellog message")
        travellog_df = pd.read_csv(
            TRAVELLOG_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        travellog_messages = get_travellog_message(travellog_df, tag=not is_test)
        logger.info("Created travellog message")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:  # 트래블로그 부 메세지 송신
        if not is_test:
            for message in travellog_messages:
                post_message_to_channel(message, TRAVELLOG_CHANNEL_ID)
        logger.info(f"Sent Message to channel {TRAVELLOG_CHANNEL_ID}")
    except Exception as e:
        logger.warning(f"Failed to send message at {TRAVELLOG_CHANNEL_ID} {e}")
        post_message_to_channel(f"travellog error: {str(e)}", TEST_CHANNEL_ID)

    try:  # Compare 트래블카드 메시지 생성
        travelcard_messages = get_compare_travel_message()
        logger.info(f"Message ready: {travelcard_messages}")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:  # 보안 모니터링 메시지 생성
        logger.info("Generating security issue message")
        security_df = pd.read_csv(
            SECURITY_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        security_messages = get_security_messages(
            security_df, tag=False
        )  # FIXME: 배포시에 not is_test 로 수정할것
        logger.info("Created security issue messages")
    except Exception as e:
        logger.error(f"Failed to generate security alerts: {e}")
        raise

    try:  # 보안 모니터링 메세지 송신
        for message in security_messages:
            post_message_to_channel(message, TEST_CHANNEL_ID)

        # if not is_test: # FIXME: 배포 테스트
        #     for message in security_messages:
        #         post_message_to_channel(message, SECURITY_CHANNEL_ID)
        logger.info(f"Sent Message to channel {SECURITY_CHANNEL_ID}")
    except Exception as e:
        logger.warning(f"Failed to send message at {SECURITY_CHANNEL_ID} {e}")
        post_message_to_channel(f"Security error: {str(e)}", TEST_CHANNEL_ID)

    try:  # 신상품 출시 메시지 송신
        product_messages = {
            "/경쟁사신용": get_product_message(
                pd.read_csv(PRODUCT_DATA_PATH),
                button_label="경쟁사신용",
                tag=not is_test,
                keywords=CREDIT_CARD_KEYWORDS,
            ),
            "/경쟁사체크": get_product_message(
                pd.read_csv(PRODUCT_DATA_PATH),
                button_label="경쟁사체크",
                tag=not is_test,
                keywords=DEBIT_CARD_KEYWORDS,
            ),
            "/원더카드": get_product_message(
                pd.read_csv(PRODUCT_DATA_PATH),
                button_label="원더카드",
                tag=not is_test,
                keywords=WONDER_CARD_FEEDBACK_KEYWORDS,
            ),
            "/JADE": get_product_message(
                pd.read_csv(PRODUCT_DATA_PATH),
                button_label="JADE",
                tag=not is_test,
                keywords=JADE_CARD_FEEDBACK_KEYWORDS,
            ),
        }
        logger.info("Created product messages")
    except Exception as e:
        logger.warning(f"Failed to generate product messages: {e}")
        product_messages = {
            "/경쟁사신용": ["경쟁사신용 메시지 생성 실패"],
            "/경쟁사체크": ["경쟁사체크 메시지 생성 실패"],
            "/원더카드": ["원더카드 메시지 생성 실패"],
            "/JADE": ["JADE 메시지 생성 실패"],
        }

    ## 메세지 저장 로직
    try:
        today_str = today_timestamp.strftime("%Y-%m-%d")
        output_dir = os.path.join("data", "messages")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"message_{today_str}.json")

        data = {
            "issue": issue_message,
            "travellog": travellog_messages,
            "travelcard": travelcard_messages,
            "security": security_messages,
            "product": product_messages,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Message saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise


async def send_message(is_test: bool = False):
    today_timestamp = datetime.now()
    if is_skip_batch(today_timestamp):
        logger.info(f"Not post today: {today_timestamp}")
        return
    try:
        await async_post_button_to_channel(JUPJUP_BUTTON, TEST_CHANNEL_ID)
        await async_post_button_to_channel(PRODUCT_BUTTON, PRODUCT_CHANNEL_ID)  # FIXME
        if is_test:
            return

        for channel_id in SUBSCRIBE_CHANNEL_IDS:
            await async_post_button_to_channel(JUPJUP_BUTTON, channel_id)
        await async_post_button_to_channel(PRODUCT_BUTTON, PRODUCT_CHANNEL_ID)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise


if __name__ == "__main__":
    logger.info("Batch started")

    data_collect()  # 데이터 수집
    logger.info("Data collection completed")

    make_message()  # 메시지 생성
    logger.info("Message created")

    asyncio.run(send_message())  # 메시지 송신
    logger.info("Message sent")

    logger.info("Batch completed")
