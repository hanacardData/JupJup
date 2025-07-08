import asyncio

from cache_util import save_message_to_cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from batch.compare_travel.make_message import get_compare_travel_message
from batch.issue.keywords import QUERIES
from batch.issue.load import collect_load_data
from batch.issue.make_message import get_issue_message
from batch.travellog.keywords import TRAVELLOG_QUERIES
from batch.travellog.load import collect_load_travellog_data
from batch.travellog.make_message import get_travellog_message


async def main():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

    # 이슈
    df_issue = collect_load_data(QUERIES, return_data=True)
    msg_issue = get_issue_message(df_issue, tag=False)
    await save_message_to_cache("issue_message", msg_issue)

    # 트래블로그
    df_travel = collect_load_travellog_data(TRAVELLOG_QUERIES, return_data=True)
    msg_travel = get_travellog_message(df_travel, tag=False)
    await save_message_to_cache("travellog_message", "\n\n".join(msg_travel))

    # 트래블카드 비교
    msg_compare = get_compare_travel_message()
    await save_message_to_cache("compare_travel_message", "\n\n".join(msg_compare))

    print("캐시에 메시지 저장 완료")


if __name__ == "__main__":
    asyncio.run(main())
