import pandas as pd
from datetime import datetime, timedelta


def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    _data = data.loc[data["is_posted"] == 0]

    today = datetime.today()
    date_criteria = today - timedelta(days=15)
    date_criteria = int(date_criteria.strftime("%Y%m%d"))
    pattern = "먹통|오류|에러|안됨|짜증|하나은행|하나카드|사용하시는|사용하는"  ## 요거는 조금 위험할 수도 있겠는데요? 논의해봐요~
    # 블로그 refine
    data_blog = _data.loc[_data["source"] == "blog"]
    data_blog = data_blog.loc[
        (~data_blog["description"].str.contains("도용", na=False))
        & (data_blog["description"].str.contains(pattern, na=False))
        & (data_blog["post_date"] >= date_criteria)
    ]

    # 카페 refine
    data_cafe = _data.loc[_data["source"] == "cafe"]
    data_cafe = data_cafe.loc[
        (data_cafe["description"].str.contains(pattern, na=False))
        | (data_cafe["title"].str.contains(pattern, na=False))
    ]

    return pd.concat([data_blog, data_cafe], ignore_index=True)


if __name__ == "__main__":
    data = pd.read_csv("data/data.csv", encoding="utf-8")
    refined_data = refine_data(data)
    print(refined_data.head())
