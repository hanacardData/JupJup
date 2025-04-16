import pandas as pd


def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[data["is_posted"] == 0]  # FIXME: 물결님 헤엎-!
    
    # 블로그 refine
    data_blog = data[data['source'] == 'blog']
    data_blog = data_blog[~data_blog['description'].str.contains('도용', na=False)]
    data_blog = data_blog[data_blog['description'].str.contains('먹통|오류|에러|안됨|짜증|하나은행|하나카드|사용하시는|사용하는', na=False)]
    data_blog = data_blog[data_blog['postdate'] >= 20250300]

    # 카페 refine
    data_cafe = data[data['source'] == 'cafe']
    data_cafe = data_cafe[~data_cafe['cafename'].str.contains('베이직피플', na=False)]
    mask = (
    data_cafe['description'].str.contains('먹통|오류|에러|안됨|짜증|하나은행|하나카드|사용하시는|사용하는', na=False) |
    data_cafe['title'].str.contains('먹통|오류|에러|안됨|짜증|하나은행|하나카드|사용하시는|사용하는', na=False)
    )
    data_cafe = data_cafe[mask]

    # 뉴스 refine
    data_news = data[data['source'] == 'news']
    data_news['postdate_dt'] = pd.to_datetime(data_news['postdate'], format='%a, %d %b %Y %H:%M:%S %z')
    data_news = data_news[data_news['postdate_dt'].dt.year == 2025]


    return pd.concat([data_blog, data_news, data_cafe], ignore_index=True)
