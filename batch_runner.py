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
    COMPARE_TRAVEL_CHANNEL_ID,
    DATA_PATH,
    SUBSCRIBE_CHANNEL_IDS,
    TEST_CHANNEL_ID,
    TRAVELLOG_CHANNEL_ID,
    TRAVELLOG_DATA_PATH,
)
from bot.services.core.post_message import post_message_to_channel
from logger import logger


def is_weekend(date: datetime.date) -> bool:
    return date.weekday() >= 5


def run_batch(is_test: bool = False):
    datetime_now = datetime.now()
    logger.info("Batch Start")

    collect_load_data(QUERIES)
    logger.info("Collection Completed")

    if is_holiday(datetime_now.strftime("%Y-%m-%d")) or is_weekend(datetime_now):
        logger.info(f"Not post today: {datetime_now}")
        return

    try:
        df = pd.read_csv(DATA_PATH, dtype={"post_date": object}, encoding="utf-8")
        message = get_issue_message(df, tag=not is_test)
        logger.info(f"Message ready: {message}")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    if is_test:
        try:
            post_message_to_channel(message, TEST_CHANNEL_ID)
            logger.info(f"Sent test message in {datetime_now}")
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
            raise
        return

    for channel_id in SUBSCRIBE_CHANNEL_IDS:
        try:
            post_message_to_channel(message, channel_id)
            logger.info(f"Sent Message to channel {channel_id} in {datetime_now}")

        except Exception as e:
            logger.warning(f"Failed to send message at {channel_id} {e}")
            post_message_to_channel(
                f"batch to {channel_id} error: {str(e)}", TEST_CHANNEL_ID
            )


def run_travellog_batch(is_test: bool = False):
    datetime_now = datetime.now()
    logger.info("Travellog Batch Start")

    collect_load_travellog_data(TRAVELLOG_QUERIES)
    logger.info("Travellog Collection Completed")

    if is_holiday(datetime_now.strftime("%Y-%m-%d")) or is_weekend(datetime_now):
        logger.info(f"Not post today: {datetime_now}")
        return

    try:
        df = pd.read_csv(
            TRAVELLOG_DATA_PATH, dtype={"post_date": object}, encoding="utf-8"
        )
        messages = get_travellog_message(df, tag=not is_test)
        logger.info(f"Message ready: {messages}")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:
        for message in messages:
            if not is_test:
                post_message_to_channel(message, TRAVELLOG_CHANNEL_ID)
            post_message_to_channel(message, TEST_CHANNEL_ID)  # 무조건 송신
        logger.info(f"Sent Message to channel {TRAVELLOG_CHANNEL_ID} in {datetime_now}")

    except Exception as e:
        logger.warning(f"Failed to send message at {TRAVELLOG_CHANNEL_ID} {e}")
        post_message_to_channel(f"travellog error: {str(e)}", TEST_CHANNEL_ID)


def run_compare_travel_batch():
    datetime_now = datetime.now()
    logger.info("Compare travel Batch Start")

    if is_holiday(datetime_now.strftime("%Y-%m-%d")) or is_weekend(datetime_now):
        logger.info(f"Not post today: {datetime_now}")
        return

    try:
        messages = get_compare_travel_message()
        logger.info(f"Message ready: {messages}")
    except Exception as e:
        logger.error(f"Failed to generate message: {e}")
        raise

    try:
        for message in messages:
            post_message_to_channel(message, COMPARE_TRAVEL_CHANNEL_ID)
        logger.info(
            f"Sent Message to channel {COMPARE_TRAVEL_CHANNEL_ID} in {datetime_now}"
        )

    except Exception as e:
        logger.warning(f"Failed to send message at {COMPARE_TRAVEL_CHANNEL_ID} {e}")
        post_message_to_channel(f"compare travel card error: {str(e)}", TEST_CHANNEL_ID)


if __name__ == "__main__":
    # run_batch(is_test=False)  # 테스트 시엔 True
    # run_travellog_batch(is_test=False)  # 테스트 시엔 True
    run_compare_travel_batch()  # 테스트 시엔 True
