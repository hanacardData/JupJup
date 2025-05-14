import json
import re
from datetime import datetime

import pandas as pd

from bot.services.core.openai_client import openai_response
from data_collect.issue.prompt import PROMPT, TEXT_INPUT
from data_collect.keywords import CARD_PRODUCTS, ISSUE_KEYWORDS
from data_collect.variables import DATA_PATH
from logger import logger


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

    def calculate_date_score(self, days: int) -> int:
        """scoring 기준 1: 날짜가 최신일수록 높은 스코어"""
        return sum([days <= 30, days <= 20, days <= 10])

    def calculate_product_score(self, text: str) -> int:
        """scoring 기준 2: 우리 상품과 관련된 키워드가 포함될수록 높은 스코어"""
        return sum(text.count(kw) for kw in self.product_keywords)

    def calculate_issue_score(self, text: str) -> int:
        """scoring 기준 3: 글의 길이 대비 issue 단어 카운트가 높을수록 높은 스코어"""
        return sum(text.count(kw) for kw in self.issue_keywords)

    def score_by_repetition(self, text: str) -> int:
        """scoring 기준 4: 모든 단어가 자주 반복될수록 낮은 스코어"""
        for kw in self.all_keywords:
            pattern = rf"({re.escape(kw)})\1{{2,}}"
            if re.search(pattern, text):
                return -1
        return 0

    def assign_percentile_score(self, series: pd.Series) -> pd.Series:
        """score를 quantile 단위로 grouping 해서 축소"""
        q90 = series.quantile(0.9)
        q80 = series.quantile(0.8)

        def score(val: float) -> int:
            return (val >= q80) + (val >= q90)

        return series.apply(score)

    def apply_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        today = datetime.today()
        post_date_dt = pd.to_datetime(df["post_date"], format="%Y%m%d", errors="coerce")
        days_diff: pd.Series = (today - post_date_dt).dt.days.fillna(999)
        date_score = days_diff.apply(self.calculate_date_score)

        _title = df["title"].fillna("")
        title_keyword_score = _title.apply(self.calculate_product_score)

        _description = df["description"].fillna("")
        _product_keyword_score_raw = _description.apply(self.calculate_product_score)
        product_keyword_score = self.assign_percentile_score(_product_keyword_score_raw)

        repetition_score = _description.apply(self.score_by_repetition)
        _issue_keyword_score_raw = _description.apply(self.calculate_issue_score)
        issue_keyword_score = self.assign_percentile_score(_issue_keyword_score_raw)

        df = df.assign(
            total_score=(
                date_score
                + title_keyword_score
                + product_keyword_score
                + repetition_score
                + issue_keyword_score
            )
        )
        return df


def extract_high_score_data(
    data: pd.DataFrame, extracted_data_count: int = 100
) -> pd.DataFrame:
    scorer = _FeedbackScorer(
        issue_keywords=ISSUE_KEYWORDS, product_keywords=CARD_PRODUCTS
    )
    _data = data[data["is_posted"] == 0]

    # 블로그 필터링
    data_blog = _data[_data["source"] == "blog"]
    data_blog = scorer.apply_scores(data_blog)
    data_blog = data_blog.sort_values(
        ["post_date", "total_score"], ascending=[False, False]
    ).iloc[: (extracted_data_count // 2)]

    # 카페 필터링
    data_cafe = _data[_data["source"] == "cafe"]
    data_cafe = scorer.apply_scores(data_cafe)
    data_cafe = data_cafe.sort_values("total_score", ascending=False).iloc[
        : (extracted_data_count // 2)
    ]

    # 병합하여 반환
    return pd.concat([data_blog, data_cafe], ignore_index=True)


def get_issue_message(data: pd.DataFrame) -> str:
    refined_data = extract_high_score_data(data)
    content = json.dumps(
        refined_data[["title", "link", "description"]].to_dict(orient="records"),
        ensure_ascii=False,
    )
    result = openai_response(
        prompt=PROMPT,
        input=TEXT_INPUT.format(
            card_products=", ".join(CARD_PRODUCTS),
            content=content,
        ),
    )
    message = (
        f"안녕하세요! 줍줍이입니다 🤗\n{datetime.today().strftime('%Y년 %m월 %d일')} 줍줍한 이슈를 공유드릴게요!\n수집한 총 {len(data)}개의 문서를 분석한 결과입니다!\n"
        + result
    )
    urls = _extract_urls(result)

    if len(urls) == 0:
        logger.warning("No URLs found in the message.")
    else:
        if len(urls) != 2:
            logger.warning("Not expected number of URLs found in the message.")
        data.loc[data["link"].isin(urls), "is_posted"] = 1

    data.to_csv(DATA_PATH, index=False, encoding="utf-8")
    return message
