"""
원하는 데이터 한개만 뽑기
"""

import json
import os

import pandas as pd
from openai import OpenAI

from secret import OPENAI_API_KEY
from variables import PROMPT, SAVE_PATH, TEXT_INPUT

client = OpenAI(api_key=OPENAI_API_KEY)


def select_post() -> dict[str, str]:
    data = pd.read_csv(os.path.join(SAVE_PATH, "data.csv"), encoding="utf-8")
    content = json.dumps(
        data[["title", "link"]].to_dict(orient="records"), ensure_ascii=False
    )
    response = client.responses.create(
        model="gpt-4o",
        instructions=PROMPT,
        input=TEXT_INPUT.format(content=content),
    )
    return data.loc[data["link"] == response.output_text].to_dict(orient="records")[0]


if __name__ == "__main__":
    select_post()
