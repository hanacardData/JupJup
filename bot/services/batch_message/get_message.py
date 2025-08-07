from typing import Literal

from batch.compare_travel.make_message import get_compare_travel_message
from batch.issue.make_message import get_issue_message
from batch.product.make_message import get_product_message
from batch.travellog.make_message import get_travellog_message


def get_batch_message(
    type_: Literal["issue", "travellog", "travelcard", "product"],
    subkey: str | None = None,
) -> list[str]:
    if type_ == "product":
        return get_product_message(subkey)
    elif type_ == "issue":
        return get_issue_message()
    elif type_ == "travellog":
        return get_travellog_message()
    elif type_ == "travelcard":
        return get_compare_travel_message()
    else:
        return ["지원하지 않는 메시지 타입입니다."]
