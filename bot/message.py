import json
import re

import pandas as pd
from openai import OpenAI

from bot.prompt import PROMPT, TEXT_INPUT
from data_collect.keywords import CARD_PRODUCTS
from data_collect.refine import refine_data
from secret import OPENAI_API_KEY
from variables import DATA_PATH

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s]+", text)
    return urls


def get_message(data: pd.DataFrame) -> str:
    refined_data = refine_data(data)
    content = json.dumps(
        refined_data[["title", "link", "description"]].to_dict(orient="records"),
        ensure_ascii=False,
    )
    response = client.responses.create(
        model="gpt-4o",
        instructions=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(CARD_PRODUCTS),
            content=content,
        ),
    )
    result = response.output_text.strip()
    urls = extract_urls(result)

    if len(urls) == 0:
        print("No URLs found in the message.")
    else:
        if len(urls) != 3:
            print("Not expected number of URLs found in the message.")
        data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(DATA_PATH, index=False, encoding="utf-8")
    return result
