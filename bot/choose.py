import json

import pandas as pd
from openai import OpenAI

from bot.prompt import PROMPT, TEXT_INPUT
from data_collect.keywords import CARD_PRODUCTS
from data_collect.refine import refine_data
from secret import OPENAI_API_KEY
from variables import DATA_PATH

client = OpenAI(api_key=OPENAI_API_KEY)


def select_post() -> str:
    """원하는 데이터 한개만 뽑기."""
    data = pd.read_csv(DATA_PATH, encoding="utf-8")
    data = refine_data(data)

    content = json.dumps(
        data[["title", "link"]].to_dict(orient="records"), ensure_ascii=False
    )
    response = client.responses.create(
        model="gpt-4o",
        instructions=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(CARD_PRODUCTS),
            content=content,
        ),
    )
    return response.output_text.strip()


if __name__ == "__main__":
    print(select_post())
