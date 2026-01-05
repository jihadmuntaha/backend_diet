from main import app
from app.services.article_fetcher import fetch_articles_api

with app.app_context():
    fetch_articles_api()
    print("FETCH API SELESAI")
