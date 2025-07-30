from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(
    jobstores={
        "default": RedisJobStore(
            jobs_key="apscheduler.jobs",
            run_times_key="apscheduler.run_times",
            host="redis",
            port=6379,
            db=0,
        )
    },
    timezone="Asia/Seoul",
)
