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


def start_scheduler():
    scheduler.start()

    redis_client = scheduler._jobstores["default"].redis
    info = redis_client.connection_pool.connection_kwargs
    print("[DEBUG] this bot where REDIS:", info)

    redis_client.set("whoami_from_bot", "네이버웍스봇")
