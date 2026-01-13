import re
from typing import Any

_TITLE_RE = re.compile(r"^제목:(.*)$", re.MULTILINE)
_CONTENT_RE = re.compile(r"^내용:(.*)$", re.MULTILINE)
_LINK_RE = re.compile(r"^링크:(.*)$", re.MULTILINE)


def _parse(m: str) -> tuple[str, str, str]:
    mt = _TITLE_RE.search(m or "")
    mc = _CONTENT_RE.search(m or "")
    ml = _LINK_RE.search(m or "")
    title = (mt.group(1) if mt else "").strip()
    content = (mc.group(1) if mc else "").strip()
    url = (ml.group(1) if ml else "").strip()
    return title, content, url


def make_geeknews_payload(
    messages: list[str], alt_text: str = "GeekNews"
) -> dict[str, Any]:
    bubbles: list[dict[str, Any]] = []

    for m in (messages or [])[1:]:
        title, content, url = _parse(m)

        title = title or "(제목 없음)"
        content = content or "(내용 없음)"

        if len(content) > 220:
            content = content[:220] + "…"

        bubbles.append(
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "14px",
                    "spacing": "10px",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "lg",
                            "wrap": True,
                        },
                        {"type": "text", "text": content, "size": "sm", "wrap": True},
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {"type": "uri", "label": "원문 보기", "uri": url},
                        },
                    ],
                },
            }
        )

    # 빈 캐러셀은 400 방지
    if not bubbles:
        return {"content": {"type": "text", "text": "오늘은 새 GeekNews가 없습니다."}}

    return {
        "content": {
            "type": "flex",
            "altText": alt_text,
            "contents": {"type": "carousel", "contents": bubbles},
        }
    }
