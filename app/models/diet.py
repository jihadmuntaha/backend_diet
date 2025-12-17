from datetime import datetime, date
from app import db

class DietRecord(db.Model):
    __tablename__ = "diet_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    record_date = db.Column(db.Date, default=date.today, index=True)

    calorie_intake = db.Column(db.Float, nullable=True)
    daily_calorie_target = db.Column(db.Float, nullable=True)

    recommended_foods = db.Column(db.Text, nullable=True)      # JSON string list
    recommended_exercises = db.Column(db.Text, nullable=True)  # JSON string list

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "calorie_intake": self.calorie_intake,
            "daily_calorie_target": self.daily_calorie_target,
            "recommended_foods": self.recommended_foods,
            "recommended_exercises": self.recommended_exercises,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
