from apscheduler.schedulers.background import BackgroundScheduler
from app.services.article_fetcher import fetch_all_articles

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Jakarta")

    # jalan setiap hari jam 06:00
    scheduler.add_job(
        fetch_all_articles,
        trigger="cron",
        hour=6,
        minute=0
    )

    scheduler.start()
