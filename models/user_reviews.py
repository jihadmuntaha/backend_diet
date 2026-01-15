from config import db
from datetime import datetime

class UserReview(db.Model):
    __tablename__ = 'user_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
