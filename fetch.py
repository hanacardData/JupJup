from typing import Literal

import requests

from logger import logger
from models.request import SearchRequest, SearchTrendRequest
from models.response import (
    AbstractResponse,
    BlogResponse,
    CafeResponse,
    NewsResponse,
    TrendsResponse,
)
from secret import CLIENT_ID, CLIENT_SECRET

TYPE_URL_MAPPER: dict[str, str] = {
    "blog": "https://openapi.naver.com/v1/search/blog.json",
    "news": "https://openapi.naver.com/v1/search/news.json",
    "cafe": "https://openapi.naver.com/v1/search/cafearticle.json",
}
TYPE_RESPONSE_MAPPER: dict[str, AbstractResponse] = {
    "blog": BlogResponse,
    "news": NewsResponse,
    "cafe": CafeResponse,
}
DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


def fetch_data(
    type: Literal["blog", "news", "cafe"],
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
) -> AbstractResponse | None:
    """
    blog, news, cafe 스크랩 코드. type이 스크랩 종류고 query가 검색어.
    """
    url = TYPE_URL_MAPPER[type]
    response_wrapper = TYPE_RESPONSE_MAPPER[type]
    headers: dict[str, str] = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    try:
        request_data = SearchRequest(
            query=query,
            display=display,
            start=start,
            sort=sort,
        )
        response = requests.get(
            url=url,
            params=request_data.model_dump(),
            headers=headers,
        )
        response.raise_for_status()
        return response_wrapper(**response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 실패: {e}")
    except ValueError as e:
        logger.error(f"응답 데이터 오류: {e}")
    except requests.HTTPError as e:
        logger.error(f"Http 오류: {e}")
    return None


def fetch_trend_data(
    startDate: str,
    endDate: str,
    timeUnit: str,
    keywordGroups: str,
    device: str | None = None,
    gender: str | None = None,
    ages: list[str] | None = None,
) -> TrendsResponse | None:
    """데이터랩 스크랩 코드. 검색어 트렌드 분석용."""
    headers: dict[str, str] = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json",
    }
    try:
        request_data = SearchTrendRequest(
            startDate=startDate,
            endDate=endDate,
            timeUnit=timeUnit,
            keywordGroups=keywordGroups,
            device=device,
            gender=gender,
            ages=ages,
        )
        response = requests.post(
            url=DATALAB_URL,
            headers=headers,
            json=request_data.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        return TrendsResponse(**response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 실패: {e}")
    except ValueError as e:
        logger.error(f"응답 데이터 오류: {e}")
    except requests.HTTPError as e:
        logger.error(f"Http 오류: {e}")
    return None


if __name__ == "__main__":
    logger.info(
        fetch_data(
            type="news",
            query="하나카드",
        )
    )

    logger.info(
        fetch_trend_data(
            type="datalab",
            startDate="2025-02-01",
            endDate="2025-02-28",
            timeUnit="date",
            keywordGroups=[
                {
                    "groupName": "하나카드",
                    "keywords": [
                        "하나카드",
                        "원더카드",
                        "제이드카드",
                        "트래블로그",
                        "트레블로그",
                    ],
                },
                {
                    "groupName": "신한카드",
                    "keywords": ["신한카드", "쏠트래블"],
                },
            ],
        )
    )
