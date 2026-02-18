import json
from typing import Literal

from agents import Agent, WebSearchTool, function_tool

from batch.fetch import fetch_data
from bot.services.cafeteria.menu import CAFETERIA_MENU


@function_tool
def fetch_data_tool(
    type: Literal["blog", "news", "cafe"],
    query: str,
) -> str:
    """네이버의 블로그, 뉴스, 카페 콘텐츠를 검색합니다.
    최신 트렌드나 실제 사용자들의 후기가 필요할 때 이 도구를 사용하세요.
    Args:
        type: 검색할 카테고리 (blog: 블로그 후기, news: 뉴스, cafe: 카페 반응)
        query: 검색어
    """
    result = fetch_data(type=type, query=query)
    return json.dumps(result.model_dump(), ensure_ascii=False)


@function_tool
def get_weekly_menu_tool() -> str:
    """구내식당 혹은 사내식당 메뉴를 가져옵니다. 구내식당의 메뉴가 필요할 때 이 도구를 사용하세요."""
    return json.dumps(CAFETERIA_MENU)


agent = Agent(
    name="줍줍이",
    instructions="당신은 하나카드의 친절한 AI Assistant '줍줍이'입니다.",
    tools=[
        get_weekly_menu_tool,
        fetch_data_tool,
        WebSearchTool(
            user_location={
                "type": "approximate",
                "country": "KR",
                "timezone": "Asia/Seoul",
            }
        ),
    ],
)
