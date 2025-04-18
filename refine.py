import pandas as pd
import re
from datetime import datetime, timedelta
from typing import List

class FeedbackScorer:
    def __init__(self, main_keywords: List[str], sub_keywords: List[str]):
        self.main_keywords = main_keywords
        self.sub_keywords = sub_keywords
        self.all_keywords = main_keywords + sub_keywords

    # scoring 기준 1: 날짜가 최신일수록 높은 스코어
    def calc_date_score(self, days: int) -> int:
        if days <= 10:
            return 3
        elif days <= 20:
            return 2
        elif days <= 30:
            return 1
        else:
            return 0

    # scoring 기준 2: 핵심 키워드가 포함될수록 높은 스코어
    def calc_keyword_score(self, text: str) -> int:
        if any(kw in text for kw in self.main_keywords):
            return 2
        elif any(kw in text for kw in self.sub_keywords):
            return 1
        return 0

    # scoring 기준 3: 글의 길이 대비 부정 단어 카운트가 높을수록 높은 스코어 
    def count_negative_keywords(self, text: str) -> int:
        return sum(text.count(kw) for kw in self.main_keywords)

    def assign_percentile_score(self, series: pd.Series) -> pd.Series:
        q90 = series.quantile(0.9)
        q80 = series.quantile(0.8)

        def score(val):
            if val >= q90:
                return 2
            elif val >= q80:
                return 1
            return 0

        return series.apply(score)

    # scoring 기준 4: 부정 단어가 자주 반복될수록 높은 스코어 
    def score_by_repetition(self, text: str) -> int:
        for kw in self.all_keywords:
            pattern = rf"({re.escape(kw)})\1{{2,}}"
            if re.search(pattern, text):
                return 1
        return 0

    def apply_scores(self, df: pd.DataFrame, date_column: str = "post_date") -> pd.DataFrame:
        today = datetime.today()
        df["post_date_dt"] = pd.to_datetime(df[date_column], format="%Y%m%d", errors="coerce")
        df["days_diff"] = (today - df["post_date_dt"]).dt.days

        df["date_score"] = df["days_diff"].apply(self.calc_date_score)
        df["keyword_score"] = df["description"].fillna("").apply(self.calc_keyword_score)
        df["repetition_score"] = df["description"].fillna("").apply(self.score_by_repetition)
        df["neg_count_raw"] = df["description"].fillna("").apply(self.count_negative_keywords)
        df["neg_count_score"] = self.assign_percentile_score(df["neg_count_raw"])

        df["total_score"] = (
            df["date_score"] +
            df["keyword_score"] +
            df["repetition_score"] +
            df["neg_count_score"]
        )
        return df
    
def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    scorer = FeedbackScorer(
        main_keywords=["먹통", "트래블로그", "트레블로그", "하나카드", "오류", "에러", "안됨", "짜증", "느려", "느림"],
        sub_keywords=["하나은행", "하나머니", '원더카드', '제이드카드', '원더 카드', '제이드 카드'],
    )

    _data = data[data["is_posted"] == 0].copy()
    today = datetime.today()
    date_criteria = int((today - timedelta(days=15)).strftime("%Y%m%d"))

    # 블로그 필터링
    data_blog = _data[(_data["source"] == "blog") &
                      (~_data["description"].str.contains("도용", na=False)) &
                      (_data["post_date"] >= date_criteria)].copy()
    data_blog = scorer.apply_scores(data_blog)
    data_blog = data_blog[data_blog["total_score"] >= 4]

    # 카페 필터링
    data_cafe = _data[(_data["source"] == "cafe") &
                      (~_data["description"].str.contains("도용", na=False)) &
                      (_data["post_date"] >= date_criteria)].copy()
    data_cafe = scorer.apply_scores(data_cafe)
    data_cafe = data_cafe[data_cafe["total_score"] >= 4]

    # 병합하여 반환
    result = pd.concat([data_blog, data_cafe], ignore_index=True)
    result["post_date"] = result["post_date"].astype("Int64").astype(str)
    return result

if __name__ == "__main__":
    data = pd.read_csv("data/data.csv", encoding="utf-8")
    refined_data = refine_data(data)
