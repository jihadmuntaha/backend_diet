import os
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin


from config import db
from models.article import Article
from app.services.sources import SOURCES


# =========================
# KEYWORDS DIET (FILTER LIST)
# =========================
PRIMARY_KEYWORDS = [
    "diet", "pola makan", "menu diet",
    "kalori", "defisit kalori",
    "menurunkan berat"
]

SECONDARY_KEYWORDS = [
    "berat badan", "protein",
    "lemak", "karbohidrat",
    "nutrisi", "gizi"
]

def generate_hash(title, url):
    raw = f"{title}{url}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()


# =========================
# SCRAPING LIST ARTIKEL
# =========================
def fetch_all_articles():
    headers = {"User-Agent": "Mozilla/5.0"}

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

                title_lower = title.lower()

                # ===== FILTER DIET (INI YANG KAMU TANYAKAN) =====
                text = title_lower
                score = 0

                for k in PRIMARY_KEYWORDS:
                    if k in text:
                        score += 2   # keyword utama bobot tinggi

                for k in SECONDARY_KEYWORDS:
                    if k in text:
                        score += 1   # keyword pendukung

                # ===== AMBANG BATAS =====
                if score < 1:
                    continue    

                link = urljoin(base_url, link)

                # ===== FILTER URL PER SUMBER =====
                if source["source_name"] == "Kompas Health":
                    if not link.startswith("https://health.kompas.com/read/"):
                        continue

                if source["source_name"] == "Detik Health":
                    if not link.startswith("https://health.detik.com/"):
                        continue
                
                if source["source_name"] == "alodokter":
                    if not link.startswith("https://www.alodokter.com/"):
                        continue    
                
                if source["source_name"] == "HelloSehat":
                    if not link.startswith("https://hellosehat.com/"):
                        continue
                
                if source["source_name"] == "KlikDokter":
                    if not link.startswith("https://www.klikdokter.com/"):
                        continue
                        
                # ===== DEDUP URL =====
                if Article.query.filter_by(article_url=link).first():
                    continue

                h = generate_hash(title, link)

                # ===== DEDUP HASH =====
                if Article.query.filter_by(content_hash=h).first():
                    continue

                article = Article(
                    title=title,
                    summary=None,
                    article_url=link,
                    image_url=None,
                    source_name=source["source_name"],
                    category="diet",
                    published_at=datetime.utcnow(),
                    content_hash=h
                )

                db.session.add(article)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("DB ERROR:", e)


# =========================
# SCRAPE ISI ARTIKEL (DETAIL)
# =========================
def scrape_article_content(url, source_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    content_paragraphs = []
    image_url = None
    summary = None

    if "kompas.com" in url:
        content_paragraphs = soup.select("div.read__content p")
        img = soup.select_one("meta[property='og:image']")
        desc = soup.select_one("meta[name='description']")

    elif "detik.com" in url:
        content_paragraphs = soup.select("div.detail__body-text p")
        img = soup.select_one("meta[property='og:image']")
        desc = soup.select_one("meta[name='description']")

    content = "\n\n".join(
        p.get_text(strip=True) for p in content_paragraphs if p.get_text(strip=True)
    )

    if img:
        image_url = img.get("content")

    if desc:
        summary = desc.get("content")

    return {
        "content": content if len(content) > 200 else None,
        "image_url": image_url,
        "summary": summary
    }

