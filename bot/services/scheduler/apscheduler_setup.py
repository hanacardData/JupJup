import redis
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(
    jobstores={
        "default": RedisJobStore(
            jobs_key="apscheduler.jobs",
            run_times_key="apscheduler.run_times",
            host="127.0.0.1",
            port=6379,
            db=0,
        )
    },
    timezone="Asia/Seoul",
)

r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
r.set("whoami_bot", "i_am_fastapi_server")
