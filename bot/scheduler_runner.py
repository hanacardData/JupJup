from bot.services.scheduler.apscheduler_setup import scheduler

if __name__ == "__main__":
    scheduler.start()
    print("🔔 APScheduler started")

    # keep alive
    import time

    while True:
        time.sleep(1)
