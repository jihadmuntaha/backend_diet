from flask import Blueprint, jsonify
from models.article import Article

article_bp = Blueprint("article", __name__)

@article_bp.route("/api/articles", methods=["GET"])
def get_articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()

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
