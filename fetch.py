import os
from typing import Literal

import requests
from dotenv import load_dotenv

from logger import init_logger
from models.request import SearchRequest
from models.response import AbstractResponse, BlogResponse, CafeResponse, NewsResponse

load_dotenv()
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
logger = init_logger()


def fetch_data(
    query: str,
    type: Literal["blog", "news", "cafe"],
    display: int | None = None,
    start: int | None = None,
    sort: str = "date",
) -> AbstractResponse | None:
    """
    blog, news, cafe 스크랩 코드. type이 스크랩 종류고 query가 검색어.
    """
    url = TYPE_URL_MAPPER[type]
    response_wrapper = TYPE_RESPONSE_MAPPER[type]
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
            headers={
                "X-Naver-Client-Id": os.environ["client_id"],
                "X-Naver-Client-Secret": os.environ["client_secret"],
            },
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
            query="하나카드",
            type="news",
        )
    )
