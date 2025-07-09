from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from bot.services.core.post_message import post_message_to_channel

scheduler = BackgroundScheduler()
scheduler.start()


def schedule_message(target_datetime: datetime, channel_id: str, message: str):
    scheduler.add_job(
        func=post_message_to_channel,
        trigger="date",
        run_date=target_datetime,
        args=[message, channel_id],
        id=f"{channel_id}-{target_datetime.timestamp()}",
        misfire_grace_time=60,
    )
