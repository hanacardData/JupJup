import os
from typing import Literal

import requests
from dotenv import load_dotenv

from logger import init_logger
from models.request import AbstractRequest, SearchRequest, SearchTrendRequest
from models.response import (
    AbstractResponse,
    BlogResponse,
    CafeResponse,
    NewsResponse,
    TrendsResponse,
)

load_dotenv()
TYPE_URL_MAPPER: dict[str, str] = {
    "blog": "https://openapi.naver.com/v1/search/blog.json",
    "news": "https://openapi.naver.com/v1/search/news.json",
    "cafe": "https://openapi.naver.com/v1/search/cafearticle.json",
    "datalab": "https://openapi.naver.com/v1/datalab/search",
}
TYPE_REQUEST_MAPPER: dict[str, AbstractRequest] = {
    "blog": SearchRequest,
    "news": SearchRequest,
    "cafe": SearchRequest,
    "datalab": SearchTrendRequest,
}
TYPE_RESPONSE_MAPPER: dict[str, AbstractResponse] = {
    "blog": BlogResponse,
    "news": NewsResponse,
    "cafe": CafeResponse,
    "datalab": TrendsResponse,
}
logger = init_logger()


def fetch_data(
    type: Literal["blog", "news", "cafe", "datalab"],
    **kwargs,
) -> AbstractResponse | None:
    """
    blog, news, cafe 스크랩 코드. type이 스크랩 종류고 query가 검색어.
    """
    url = TYPE_URL_MAPPER[type]
    request_wrapper = TYPE_REQUEST_MAPPER[type]
    response_wrapper = TYPE_RESPONSE_MAPPER[type]
    headers: dict[str, str] = {
        "X-Naver-Client-Id": os.environ["client_id"],
        "X-Naver-Client-Secret": os.environ["client_secret"],
    }
    try:
        request_data = request_wrapper(**kwargs)
        if type == "datalab":
            headers.update({"Content-Type": "application/json"})
            response = requests.post(
                url=url,
                headers=headers,
                json=request_data.model_dump(exclude_none=True),
            )
        else:
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


if __name__ == "__main__":
    logger.info(
        fetch_data(
            type="news",
            query="하나카드",
        )
    )

    logger.info(
        fetch_data(
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
