import os
from datetime import datetime

# from apscheduler.jobstores.json import JSONJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from bot.services.core.post_message import post_message_to_channel

jobstore_dir = "jobs"
jobstore_file = "jobs.json"
os.makedirs(jobstore_dir, exist_ok=True)

scheduler = BackgroundScheduler()
# scheduler.add_jobstore(JSONJobStore(path=os.path.join(jobstore_dir, jobstore_file)))
scheduler.start()


def schedule_message(dt: datetime, message: str, channel_id: str) -> None:
    scheduler.add_job(
        func=post_message_to_channel,
        trigger="date",
        run_date=dt,
        args=[message, channel_id],
        id=f"{channel_id}-{dt.timestamp()}",
        misfire_grace_time=60,
    )
