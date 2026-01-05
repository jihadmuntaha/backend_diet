from datetime import datetime
from config import db

class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)

    image_url = db.Column(db.Text)
    article_url = db.Column(db.Text, nullable=False)

    source_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    language = db.Column(db.String(5), default="id")

    published_at = db.Column(db.DateTime)
    content_hash = db.Column(db.String(64), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
