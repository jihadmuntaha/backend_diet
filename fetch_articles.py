from main import app
from app.services.article_fetcher import fetch_all_articles


with app.app_context():
    fetch_all_articles()
    
    print("FETCH ARTIKEL SELESAI")
