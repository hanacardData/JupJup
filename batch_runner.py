from datetime import datetime

import pandas as pd
from holidayskr import is_holiday

from batch.compare_travel.make_message import get_compare_travel_message
from batch.issue.keywords import QUERIES
from batch.issue.load import collect_load_data
from batch.issue.make_message import get_issue_message
from batch.travellog.keywords import TRAVELLOG_QUERIES
from batch.travellog.load import collect_load_travellog_data
from batch.travellog.make_message import get_travellog_message
from batch.variables import (
    DATA_PATH,
    TEST_CHANNEL_ID,
    TRAVELLOG_CHANNEL_ID,
    TRAVELLOG_DATA_PATH,
)
from bot.services.core.post_message import post_message_to_channel
from logger import logger


def is_skip_batch(date: datetime) -> bool:
    return is_holiday(date.strftime("%Y-%m-%d")) or date.weekday() >= 5


def data_collect():
    collect_load_data(QUERIES)
    logger.info("Issue Data Collection Completed")

    collect_load_travellog_data(TRAVELLOG_QUERIES)
    logger.info("Travellog Data Collection Completed")


def make_message(is_test: bool = False):
    if is_skip_batch(datetime.now()):
        logger.info(f"Not post today: {datetime.now()}")
        return

    try:  # Issue 메시지 생성
        logger.info("Generating issue message")
        issue_df = pd.read_csv(DATA_PATH, dtype={"post_date": object}, encoding="utf-8")
        message = get_issue_message(issue_df, tag=not is_test)
        # FIXME: message save 로직 추가할것
        logger.info("Created issue message")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:  # 트래블로그 메시지 생성
        logger.info("Generating travellog message")
        travellog_df = pd.read_csv(
            TRAVELLOG_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        messages = get_travellog_message(travellog_df, tag=not is_test)
        # FIXME: message save 로직 추가할것
        logger.info("Created travellog message")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:  # 트래블로그 부 메세지 송신
        for message in messages:
            if not is_test:
                post_message_to_channel(message, TRAVELLOG_CHANNEL_ID)
            post_message_to_channel(message, TEST_CHANNEL_ID)  # 무조건 송신
        logger.info(f"Sent Message to channel {TRAVELLOG_CHANNEL_ID}")

    except Exception as e:
        logger.warning(f"Failed to send message at {TRAVELLOG_CHANNEL_ID} {e}")
        post_message_to_channel(f"travellog error: {str(e)}", TEST_CHANNEL_ID)

    try:  # Compare 트래블카드 메시지 생성
        messages = get_compare_travel_message()
        logger.info(f"Message ready: {messages}")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise


if __name__ == "__main__":
    logger.info("Batch started")
    data_collect()  # 데이터 수집
    logger.info("Data collection completed")
    make_message(is_test=True)  # 메시지 생성
