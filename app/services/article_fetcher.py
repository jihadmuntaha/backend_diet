import os
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

from config import db
from models.article import Article
from app.services.sources import SOURCES


def generate_hash(title, url):
    raw = f"{title}{url}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()


# =========================
# SCRAPING ARTIKEL
# =========================
def fetch_all_articles():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for source in SOURCES:
        if source["type"] != "scraping":
            continue

        for base_url in source["urls"]:
            try:
                r = requests.get(base_url, headers=headers, timeout=10)
                r.raise_for_status()
            except Exception as e:
                print("SCRAPE ERROR:", base_url, e)
                continue

            soup = BeautifulSoup(r.text, "lxml")

            for a in soup.select("a[href]"):
                title = a.get_text(strip=True)
                link = a.get("href")

                # basic validation
                if not title or len(title) < 30:
                    continue

                link = urljoin(base_url, link)

                # ===== FILTER URL ARTIKEL =====
                if source["source_name"] == "Kompas Health":
                    if not link.startswith("https://health.kompas.com/read/"):
                        continue

                if source["source_name"] == "Detik Health":
                    if not link.startswith("https://health.detik.com/"):
                        continue

                # ===== DEDUP BERDASARKAN URL =====
                if Article.query.filter_by(article_url=link).first():
                    continue

                h = generate_hash(title, link)

                # ===== DEDUP BERDASARKAN HASH =====
                if Article.query.filter_by(content_hash=h).first():
                    continue

                article = Article(
                    title=title,
                    summary=None,
                    article_url=link,
                    image_url=None,
                    source_name=source["source_name"],
                    published_at=datetime.utcnow(),
                    content_hash=h
                )

                db.session.add(article)

            # commit per source (lebih aman)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("DB ERROR:", e)


# =========================
# API (NEWSAPI)
# =========================
def fetch_articles_api():
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return

    params = {
        "q": "diet OR nutrisi OR gizi OR olahraga OR penurunan berat badan",
        "language": "id",
        "pageSize": 20,
        "sortBy": "publishedAt",
        "apiKey": api_key
    }

    r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
    data = r.json()

    if data.get("status") != "ok":
        return

    KEYWORDS = [
        "diet", "nutrisi", "gizi",
        "kalori", "berat badan",
        "olahraga", "protein", "lemak"
    ]

    for item in data.get("articles", []):
        title = item.get("title")
        summary = item.get("description") or ""
        link = item.get("url")

        if not title or not link:
            continue

        text = f"{title} {summary}".lower()

        if not any(k in text for k in KEYWORDS):
            continue

        if Article.query.filter_by(article_url=link).first():
            continue

        article = Article(
            title=title,
            summary=summary,
            article_url=link,
            image_url=item.get("urlToImage"),
            source_name="NewsAPI",
            category="diet",
            published_at=datetime.fromisoformat(
                item["publishedAt"].replace("Z", "+00:00")
            ),
            content_hash=generate_hash(title, link)
        )

        db.session.add(article)

    db.session.commit()

