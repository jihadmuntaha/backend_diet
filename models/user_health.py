from config import db
from datetime import datetime

class UserHealth(db.Model):
    __tablename__ = "user_health"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tinggi_badan = db.Column(db.Float, nullable=False)  # in cm
    berat_badan = db.Column(db.Float, nullable=False)   # in kg
    bmi = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)