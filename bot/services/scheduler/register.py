from datetime import datetime

import pytz

from bot.services.core.post_message import post_message_to_channel
from bot.services.scheduler.apscheduler_setup import scheduler


def register_schedule(channel_id: str, content: str) -> str:
    parts = content.strip().split()
    if len(parts) < 2:
        return "⚠️ 등록 형식이 잘못되었습니다. 예시: /스케줄등록 2025-07-30 15:00 회의"

    # TODO: 과거를 등록하는 경우 예외 처리
    date_str, time_str, *msg_parts = parts
    message = " ".join(msg_parts)

    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt = pytz.timezone("Asia/Seoul").localize(dt)
    try:
        scheduler.add_job(
            post_message_to_channel,
            "date",
            run_date=dt,
            args=[f"⏰ 알림: {message}", channel_id],
            id=f"{channel_id}:{dt.timestamp()}",
        )
    except Exception as e:
        return f"{str(e)}"
    return f"✅ {date_str} {time_str}에 예약 완료!"
