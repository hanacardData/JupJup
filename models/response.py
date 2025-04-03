import re

from pydantic import BaseModel, Field, field_serializer


def remove_html_tags(text: str) -> str:
    return re.sub(r"<.*?>", "", text) if text else text


class AbstractResponse(BaseModel):
    def to_items(self) -> list[dict[str, str]]:
        if not hasattr(self, "items"):
            raise ValueError("items not exists.")
        return [item.model_dump() for item in self.items]


class BaseItem(BaseModel):
    @field_serializer("title", "description", check_fields=False)
    def remove_html(self, value: str) -> str:
        return remove_html_tags(value)


class BlogItem(BaseItem):
    title: str = Field(
        ...,
        title="포스트 제목",
        description="검색어와 일치하는 부분은 <b> 태그로 감싸짐",
    )
    link: str = Field(..., title="포스트 URL")
    description: str = Field(
        ...,
        title="포스트 요약",
        description="검색어와 일치하는 부분은 <b> 태그로 감싸짐",
    )
    bloggername: str = Field(..., title="블로그 이름")
    bloggerlink: str = Field(..., title="블로그 주소")
    postdate: str = Field(..., title="작성 날짜")


class BlogResponse(AbstractResponse):
    lastBuildDate: str = Field(..., title="검색 결과 생성 시간")
    total: int = Field(..., title="총 검색 결과 개수")
    start: int = Field(..., title="검색 시작 위치")
    display: int = Field(..., title="표시 개수")
    items: list[BlogItem] = Field(..., title="검색 결과 목록")


class NewsItem(BaseItem):
    title: str = Field(
        ..., title="뉴스 제목", description="검색어와 일치하는 부분은 <b> 태그로 감싸짐"
    )
    originallink: str = Field(..., title="기사 원문 URL")
    link: str = Field(..., title="네이버 뉴스 URL 또는 원문 URL")
    description: str = Field(
        ..., title="기사 요약", description="검색어와 일치하는 부분은 <b> 태그로 감싸짐"
    )
    pubDate: str = Field(..., title="기사 제공 시간")


class NewsResponse(AbstractResponse):
    lastBuildDate: str = Field(..., title="검색 결과 생성 시간")
    total: int = Field(..., title="총 검색 결과 개수")
    start: int = Field(..., title="검색 시작 위치")
    display: int = Field(..., title="표시 개수")
    items: list[NewsItem] = Field(..., title="검색 결과 목록")


class CafeItem(BaseItem):
    title: str = Field(
        ...,
        title="게시글 제목",
        description="검색어와 일치하는 부분은 <b> 태그로 감싸짐",
    )
    link: str = Field(..., title="게시글 URL")
    description: str = Field(
        ...,
        title="게시글 요약",
        description="검색어와 일치하는 부분은 <b> 태그로 감싸짐",
    )
    cafename: str = Field(..., title="카페 이름")
    cafeurl: str = Field(..., title="카페 URL")


class CafeResponse(AbstractResponse):
    lastBuildDate: str = Field(..., title="검색 결과 생성 시간")
    total: int = Field(..., title="총 검색 결과 개수")
    start: int = Field(..., title="검색 시작 위치")
    display: int = Field(..., title="표시 개수")
    items: list[CafeItem] = Field(..., title="검색 결과 목록")


class TrendData(BaseModel):
    period: str = Field(..., title="구간 시작 날짜", description="yyyy-mm-dd 형식")
    ratio: float = Field(
        ...,
        title="검색량 상대적 비율",
        description="가장 큰 값을 100으로 설정한 상댓값",
    )


class TrendResult(BaseModel):
    title: str = Field(..., title="주제어")
    keywords: list[str] = Field(..., title="주제어에 해당하는 검색어 목록")
    data: list[TrendData] = Field(..., title="검색 데이터 목록")


class TrendsResponse(BaseModel):
    startDate: str = Field(
        ..., title="조회 기간 시작 날짜", description="yyyy-mm-dd 형식"
    )
    endDate: str = Field(
        ..., title="조회 기간 종료 날짜", description="yyyy-mm-dd 형식"
    )
    timeUnit: str = Field(
        ..., title="구간 단위", description="date, week, month 중 하나"
    )
    results: list[TrendResult] = Field(..., title="검색 결과 목록")
