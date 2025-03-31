from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """blog, news, cafe API request
    blog: https://developers.naver.com/docs/serviceapi/search/blog/blog.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
    news: https://developers.naver.com/docs/serviceapi/search/news/news.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
    cafe: https://developers.naver.com/docs/serviceapi/search/cafearticle/cafearticle.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
    """

    query: str = Field(..., description="검색어")
    display: int | None = Field(
        10,
        ge=1,
        le=100,
        description="한 번에 표시할 검색 결과 개수 (기본값: 10, 최댓값: 100)",
    )
    start: int | None = Field(
        1, ge=1, le=1000, description="검색 시작 위치 (기본값: 1, 최댓값: 1000)"
    )
    sort: str | None = Field(
        "date",
        pattern="^(sim|date)$",
        description="검색 결과 정렬 방법 (sim: 정확도순, date: 날짜순)",
    )


class KeywordGroup(BaseModel):
    groupName: str = Field(..., description="검색어 묶음을 대표하는 이름")
    keywords: list[str] = Field(
        ..., min_length=1, max_length=20, description="최대 20개의 검색어"
    )


class SearchTrendRequest(BaseModel):
    """데이터랩 API 요청
    https://developers.naver.com/docs/serviceapi/datalab/search/search.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0.
    """

    startDate: str = Field(..., description="yyyy-mm-dd 형식, 2016-01-01 이후")
    endDate: str = Field(..., description="yyyy-mm-dd 형식")
    timeUnit: str = Field(
        ...,
        pattern="^(date|week|month)$",
        description="date(일간), week(주간), month(월간)",
    )
    keywordGroups: list[KeywordGroup] = Field(
        ..., min_length=1, max_length=5, description="최대 5개까지 설정 가능"
    )
    device: str | None = Field(
        None, pattern="^(pc|mo)?$", description="pc(PC), mo(모바일), 설정 없으면 전체"
    )
    gender: str | None = Field(
        None, pattern="^(m|f)?$", description="m(남성), f(여성), 설정 없으면 전체"
    )
    ages: list[str] | None = Field(
        None, description="1~11까지의 연령 그룹 배열 (설정 없으면 전체)"
    )
