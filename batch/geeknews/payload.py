import re

_TITLE_RE = re.compile(r"^제목:(.*)$", re.MULTILINE)
_CONTENT_RE = re.compile(r"^내용:(.*)$", re.MULTILINE)
_LINK_RE = re.compile(r"^링크:(.*)$", re.MULTILINE)


def make_geeknews_flexible_payload(messages: list[str]) -> dict:
    """
    기존 messages(list[str])를 카드 캐러셀로 변환.
    messages 예: ["geeknews", "제목:...\n내용:...\n링크:...", ...]
    """
    bubbles = []

    # 첫 원소 "geeknews"는 헤더라서 제외
    for m in messages[1:]:
        title = ""
        content = ""
        url = ""

        mt = _TITLE_RE.search(m)
        mc = _CONTENT_RE.search(m)
        ml = _LINK_RE.search(m)

        if mt:
            title = mt.group(1).strip()
        if mc:
            content = mc.group(1).strip()
        if ml:
            url = ml.group(1).strip()

        if not title and not content and not url:
            continue

        if len(content) > 220:
            content = content[:220] + "…"

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#0AA37F",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": "GeekNews",
                        "weight": "bold",
                        "size": "md",
                        "color": "#FFFFFF",
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "8px",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": title or "(제목 없음)",
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                    },
                    {
                        "type": "text",
                        "text": content or "(내용 없음)",
                        "size": "sm",
                        "wrap": True,
                        "color": "#333333",
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#22C55E",
                        "action": {
                            "type": "uri",
                            "label": "link",
                            "uri": url or "https://news.hada.io/",
                        },
                    }
                ],
            },
        }
        bubbles.append(bubble)

    return {"type": "carousel", "contents": bubbles}
