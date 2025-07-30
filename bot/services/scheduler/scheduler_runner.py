import asyncio

from bot.services.scheduler.apscheduler_setup import scheduler


async def start():
    try:
        scheduler.start()
        print("APScheduler started")
    except Exception as e:
        print(f"APScheduler failed to start: {e}")

    while True:
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(start())
