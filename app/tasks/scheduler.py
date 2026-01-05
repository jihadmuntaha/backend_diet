from apscheduler.schedulers.background import BackgroundScheduler
from app.services.article_fetcher import fetch_all_articles

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(fetch_all_articles, "interval", days=1)
    scheduler.start()