from config import db
from datetime import datetime  

class Recommendations(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scan_id = db.Column(db.Integer, db.ForeignKey('posture_scans.id'), nullable=False)
    rekomendasi_makanan = db.Column(db.Text, nullable=False)
    rekomendasi_olahraga = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scan_id": self.scan_id,
            "rekomendasi_makanan": self.rekomendasi_makanan,
            "rekomendasi_olahraga": self.rekomendasi_olahraga,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }