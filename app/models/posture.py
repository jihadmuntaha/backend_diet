from datetime import datetime
from app import db

class PostureMeasurement(db.Model):
    __tablename__ = "posture_measurements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # snapshot body metrics saat pengukuran
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)

    posture_category = db.Column(db.String(50), nullable=True)
    posture_score = db.Column(db.Float, nullable=True)  # 0–100

    # keypoints Mediapipe (JSON string)
    keypoints = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "posture_category": self.posture_category,
            "posture_score": self.posture_score,
            "keypoints": self.keypoints,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
