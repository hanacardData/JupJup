import os
import re

import pandas as pd


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s]+", text)
    return urls


def read_csv(file_path: str) -> pd.DataFrame:
    if os.path.exists(file_path):
        return pd.read_csv(file_path, encoding="utf-8")
    return pd.DataFrame()
