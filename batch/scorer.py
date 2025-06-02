import re
from datetime import datetime

import pandas as pd


class FeedbackScorer:
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
        """scoring 기준 2: 우리 상품과 관련된 키워드가 포함되면 1 아니면 0"""
        return int(any(kw in text for kw in self.product_keywords))

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
        post_days_diff: pd.Series = (today - post_date_dt).dt.days.fillna(999)
        post_date_score = post_days_diff.apply(self.calculate_date_score)

        scrap_date_dt = pd.to_datetime(
            df["scrap_date"], format="%Y%m%d", errors="coerce"
        )
        scrap_days_diff: pd.Series = (today - scrap_date_dt).dt.days
        scrap_date_score = scrap_days_diff.apply(self.calculate_date_score)

        _title = df["title"].fillna("")
        title_keyword_score = _title.apply(self.calculate_product_score)
        repetition_title_score = _title.apply(self.score_by_repetition)

        _description = df["description"].fillna("")
        _product_keyword_score_raw = _description.apply(self.calculate_product_score)
        product_keyword_score = self.assign_percentile_score(_product_keyword_score_raw)
        repetition_description_score = _description.apply(self.score_by_repetition)

        _issue_keyword_score_raw = _description.apply(self.calculate_issue_score)
        issue_keyword_score = self.assign_percentile_score(_issue_keyword_score_raw)

        df = df.assign(
            total_score=(
                title_keyword_score
                * (
                    post_date_score
                    + scrap_date_score
                    + product_keyword_score
                    + repetition_title_score
                    + repetition_description_score
                    + issue_keyword_score
                )
            )
        )
        return df


def extract_high_score_data(
    data: pd.DataFrame,
    issue_keywords: list[str],
    product_keywords: list[str],
    extracted_data_count: int,
) -> pd.DataFrame:
    scorer = FeedbackScorer(
        issue_keywords=issue_keywords,
        product_keywords=product_keywords,
    )
    _data = data.loc[data["is_posted"] == 0]

    # 블로그 필터링
    data_blog = _data.loc[_data["source"] == "blog"]
    data_blog = scorer.apply_scores(data_blog)
    data_blog = (
        data_blog.loc[data_blog["total_score"] > 0]
        .sort_values(["post_date", "total_score"], ascending=[False, False])
        .iloc[: min((extracted_data_count // 2), len(data_blog))]
    )

    # 카페 필터링
    data_cafe = _data.loc[_data["source"] == "cafe"]
    data_cafe = scorer.apply_scores(data_cafe)
    data_cafe = (
        data_cafe.loc[data_cafe["total_score"] > 0]
        .sort_values(["scrap_date", "total_score"], ascending=[False, False])
        .iloc[: min((extracted_data_count // 2), len(data_cafe))]
    )

    # 병합하여 반환
    return pd.concat([data_blog, data_cafe], ignore_index=True)
