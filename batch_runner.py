import pandas as pd

from bot.post_message import post_message
from data_collect.keywords import QUERIES
from data_collect.load import collect_load_data
from variables import DATA_PATH


def run_all():
    print("Batch Start")

    collect_load_data(QUERIES)
    print("Collection Completed.")

    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    post_message(data=df, is_test=False)  # test 시에는 True로 변경
    print("Sent Message")


if __name__ == "__main__":
    run_all()
