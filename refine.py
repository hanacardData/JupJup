import pandas as pd


def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    _data = data.loc[data["is_posted"] == 0]
    ## TODO: 현재 시점에 따라 시점을 변경하는 코드 작성
    ## 예, 20250416 이니까 -> 15일전을 기준으로 20250401이라는 형 구하기
    ## np.issubdtype(_data['post_date'], np.int | np.float)에 따라서 숫자형, 아니면 문자형으로 반환하여 date_criteria 로 할당

    data_criteria = 20250401
    pattern = "먹통|오류|에러|안됨|짜증|하나은행|하나카드|사용하시는|사용하는"  ## 요거는 조금 위험할 수도 있겠는데요? 논의해봐요~
    # 블로그 refine
    data_blog = _data.loc[_data["source"] == "blog"]
    data_blog = data_blog.loc[
        (~data_blog["description"].str.contains("도용", na=False))
        & (data_blog["description"].str.contains(pattern, na=False))
        & (data_blog["post_date"] >= data_criteria)
    ]

    # 카페 refine
    data_cafe = _data.loc[_data["source"] == "cafe"]
    data_cafe = data_cafe.loc[
        (data_cafe["description"].str.contains(pattern, na=False))
        | (data_cafe["title"].str.contains(pattern, na=False))
    ]

    # 뉴스 refine
    data_news = _data[_data["source"] == "news"]
    data_news = data_news[data_news["post_date"] >= data_criteria]

    return pd.concat([data_blog, data_news, data_cafe], ignore_index=True)


if __name__ == "__main__":
    data = pd.read_csv("data/data.csv", encoding="utf-8")
    refined_data = refine_data(data)
    print(refined_data.head())
