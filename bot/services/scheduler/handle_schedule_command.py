from datetime import datetime

import pytz

from bot.services.core.post_message import async_post_message_to_channel

from .apscheduler_setup import scheduler


def handle_schedule_command(customer_id: str, channel_id: str, content: str) -> str:
    try:
        parts = content.strip().split()
        if len(parts) < 3:
            raise ValueError("형식 오류")

        date_str, time_str, *msg_parts = parts
        message = " ".join(msg_parts)

        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt = pytz.timezone("Asia/Seoul").localize(dt)

        scheduler.add_job(
            async_post_message_to_channel,
            "date",
            run_date=dt,
            args=[f"⏰ 알림: {message}", channel_id],
            id=f"{customer_id}:{dt.timestamp()}",
        )

        return f"✅ {date_str} {time_str}에 예약 완료!"
    except Exception:
        return "⚠️ 등록 형식이 잘못되었습니다. 예시: 2025-08-01 10:30 회의"
