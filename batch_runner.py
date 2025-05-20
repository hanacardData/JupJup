from datetime import datetime

import pandas as pd
from holidayskr import is_holiday

from bot.services.core.post_message import post_message_to_channel
from data_collect.issue.make_message import get_issue_message
from data_collect.keywords import QUERIES
from data_collect.load import collect_load_data
from data_collect.variables import DATA_PATH, SUBSCRIBE_CHANNEL_IDS, TEST_CHANNEL_ID
from logger import logger


def is_weekend(date: datetime.date) -> bool:
    return date.weekday() >= 5


def run_all(is_test: bool = False):
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


if __name__ == "__main__":
    run_all(is_test=True)  # 테스트 시엔 True
