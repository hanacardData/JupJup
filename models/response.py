from pydantic import BaseModel, Field


class AbstractResponse(BaseModel):
    pass


class BlogItem(BaseModel):
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


class NewsItem(BaseModel):
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


class CafeItem(BaseModel):
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
