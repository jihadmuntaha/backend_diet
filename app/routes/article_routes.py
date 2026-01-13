from flask import Blueprint, jsonify, request
from models import article
from models.article import Article
from config import db
from app.services.article_fetcher import PRIMARY_KEYWORDS, scrape_article_content


article_bp = Blueprint("article", __name__)

@article_bp.route("/api/articles", methods=["GET"])
def get_articles():
    q = request.args.get("q")

    query = Article.query

    if q:
        query = query.filter(Article.title.ilike(f"%{q}%"))

    articles = query.order_by(Article.created_at.desc()).all()

    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "summary": a.summary,
            "image": a.image_url,
            "date": a.published_at.isoformat() if a.published_at else None
        }
        for a in articles
    ])

@article_bp.route("/api/articles/<int:article_id>", methods=["GET"])
def get_article_detail(article_id):
    article = Article.query.get_or_404(article_id)

    if not article.content:
        result = scrape_article_content(article.article_url, article.source_name)
        
        if result and result.get("content"):
            article.content = result["content"]
            article.image_url = article.image_url or result.get("image_url")
            article.summary = article.summary or result.get("summary")

            db.session.commit()

    return jsonify({
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "image_url": article.image_url,
        "source_name": article.source_name,
        "published_at": article.published_at.isoformat() if article.published_at else None
    })
    
    
from sqlalchemy.sql import func

@article_bp.route("/api/articles/home", methods=["GET"])
def home_articles():
    articles = (
        Article.query
        .filter(Article.category == "diet")
        .order_by(func.random())
        .limit(5)
        .all()
    )

    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "image_url": a.image_url,
            "published_at": a.published_at.strftime("%d %B %Y")
        }
        for a in articles
    ])
