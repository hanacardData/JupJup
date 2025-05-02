from datetime import datetime

import pandas as pd
from holidayskr import is_holiday

from bot.issue import post_issue_message
from data_collect.keywords import QUERIES
from data_collect.load import collect_load_data
from logger import logger
from variables import DATA_PATH


def run_all():
    datetime_now = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Batch Start: {datetime_now}")

    collect_load_data(QUERIES)
    logger.info(f"Collection Completed: {datetime_now}")

    if is_holiday(datetime_now):
        logger.info(f"Today is a holiday: {datetime_now}")
        return

    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    post_issue_message(data=df, is_test=False)  # test 시에는 True로 변경
    logger.info("Sent Message")


if __name__ == "__main__":
    run_all()
