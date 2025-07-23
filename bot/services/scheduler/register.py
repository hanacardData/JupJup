from datetime import datetime

import pytz

from bot.services.scheduler.schedule import schedule_message

# 테스트 채널 제한 여부 (테스트 시에만 True)
TEST_MODE = True


def handle_schedule_command(channel_id: str, content: str) -> str:
    try:
        # 예: "/스케줄등록 2025-07-01 14:30 회의"
        parts = content.strip().split()
        if len(parts) < 4:
            raise ValueError("형식 오류")

        _, date_str, time_str, *msg_parts = parts
        message = " ".join(msg_parts)

        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt = pytz.timezone("Asia/Seoul").localize(dt)

        schedule_message(dt, channel_id, f"⏰ 알림: {message}")
        return f"✅ {date_str} {time_str}에 알림을 등록했어요!"
    except Exception:
        return "⚠️ 등록 형식이 잘못되었습니다. 예시: /스케줄등록 2025-07-01 14:30 회의"
