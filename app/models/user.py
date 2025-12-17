from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    posture_category = db.Column(db.String(50), nullable=True)  # normal, kyphosis, lordosis, scoliosis, dsb.
    activity_level = db.Column(db.String(50), nullable=True)    # sedentary, light, moderate, heavy
    target_weight = db.Column(db.Float, nullable=True)
    diet_type = db.Column(db.String(50), nullable=True)         # cutting, bulking, maintenance, dsb.
    allergies = db.Column(db.Text, nullable=True)               # JSON string list alergi

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    postures = db.relationship(
        "PostureMeasurement",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    diets = db.relationship(
        "DietRecord",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "posture_category": self.posture_category,
            "activity_level": self.activity_level,
            "target_weight": self.target_weight,
            "diet_type": self.diet_type,
            "allergies": self.allergies,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
