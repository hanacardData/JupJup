import pandas as pd

from bot.post_message_bot import post_message
from data_collect.keywords import QUERIES
from data_collect.load import collect_load_data
from data_collect.refine import refine_data
from variables import DATA_PATH


def run_all():
    print("Batch Start")

    collect_load_data(QUERIES)
    print("Collection Completed.")

    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    refined = refine_data(df)
    refined.to_csv(DATA_PATH, index=False, encoding="utf-8")
    print("Refining Completed.")

    post_message()
    print("Sent Message")


if __name__ == "__main__":
    run_all()
