import json
import re
from datetime import datetime

import pandas as pd
from openai import OpenAI

from bot.prompt import PROMPT, TEXT_INPUT
from data_collect.keywords import CARD_PRODUCTS, ISSUE_KEYWORDS
from secret import OPENAI_API_KEY
from variables import DATA_PATH

client = OpenAI(api_key=OPENAI_API_KEY)


def _extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s]+", text)
    return urls


class _FeedbackScorer:
    def __init__(
        self,
        issue_keywords: list[str],
        product_keywords: list[str],
    ):
        self.issue_keywords = issue_keywords
        self.product_keywords = product_keywords
        self.all_keywords = issue_keywords + product_keywords

    # scoring 기준 1: 날짜가 최신일수록 높은 스코어
    def calc_date_score(self, days: int) -> int:
        return sum([days <= 30, days <= 20, days <= 10])

    # scoring 기준 2: 핵심 키워드가 포함될수록 높은 스코어
    def calc_keyword_score(self, text: str) -> int:
        if any(kw in text for kw in self.issue_keywords):
            return 2
        elif any(kw in text for kw in self.product_keywords):
            return 1
        return 0

    # scoring 기준 3: 글의 길이 대비 부정 단어 카운트가 높을수록 높은 스코어
    def count_negative_keywords(self, text: str) -> int:
        return sum(text.count(kw) for kw in self.issue_keywords)

    def assign_percentile_score(self, series: pd.Series) -> pd.Series:
        q90 = series.quantile(0.9)
        q80 = series.quantile(0.8)

        def score(val: float):
            return (val >= q80) + (val >= q90)

        return series.apply(score)

    # scoring 기준 4: 부정 단어가 자주 반복될수록 높은 스코어
    def score_by_repetition(self, text: str) -> int:
        for kw in self.all_keywords:
            pattern = rf"({re.escape(kw)})\1{{2,}}"
            if re.search(pattern, text):
                return 1
        return 0

    def apply_scores(
        self, df: pd.DataFrame, date_column: str = "post_date"
    ) -> pd.DataFrame:
        today = datetime.today()
        df = df.assign(
            post_date_dt=pd.to_datetime(
                df[date_column], format="%Y%m%d", errors="coerce"
            )
        )
        df = df.assign(days_diff=(today - df["post_date_dt"]).dt.days)

        df = df.assign(
            date_score=df["days_diff"].apply(self.calc_date_score),
            keyword_score=df["description"].fillna("").apply(self.calc_keyword_score),
            repetition_score=df["description"]
            .fillna("")
            .apply(self.score_by_repetition),
            neg_count_raw=df["description"]
            .fillna("")
            .apply(self.count_negative_keywords),
        )
        df = df.assign(
            neg_count_score=self.assign_percentile_score(df["neg_count_raw"]),
        )

        df = df.assign(
            total_score=(
                df["date_score"]
                + df["keyword_score"]
                + df["repetition_score"]
                + df["neg_count_score"]
            )
        )
        return df


def _refine_data(data: pd.DataFrame) -> pd.DataFrame:
    scorer = _FeedbackScorer(
        issue_keywords=ISSUE_KEYWORDS, product_keywords=CARD_PRODUCTS
    )
    _data = data[data["is_posted"] == 0]

    # 블로그 필터링
    data_blog = _data[_data["source"] == "blog"]
    data_blog = scorer.apply_scores(data_blog)
    data_blog = data_blog.sort_values(
        ["post_date", "total_score"], ascending=[False, False]
    ).iloc[:50]

    # 카페 필터링
    data_cafe = _data[_data["source"] == "cafe"]
    data_cafe = scorer.apply_scores(data_cafe)
    data_cafe = data_cafe.sort_values("total_score", ascending=False).iloc[:50]

    # 병합하여 반환
    return pd.concat([data_blog, data_cafe], ignore_index=True)


def get_message(data: pd.DataFrame) -> str:
    refined_data = _refine_data(data)
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
    urls = _extract_urls(result)

    if len(urls) == 0:
        print("No URLs found in the message.")
    else:
        if len(urls) != 3:
            print("Not expected number of URLs found in the message.")
        data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(DATA_PATH, index=False, encoding="utf-8")
    return result
