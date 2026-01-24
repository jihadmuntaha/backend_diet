from config import db
from datetime import datetime

class PostureScan(db.Model):
    __tablename__ = "posture_scans"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    posture_overall = db.Column(db.String(50))
    lengan_angle = db.Column(db.Float)
    lengan_status = db.Column(db.String(50))
    paha_angle = db.Column(db.Float)
    paha_status = db.Column(db.String(50))
    perut_angle = db.Column(db.Float)
    perut_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi rekomendasi (one scan → many recommendations?)
    recommendations = db.relationship("Recommendations", backref="scan", lazy=True)
