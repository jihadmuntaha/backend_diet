from config import db
from datetime import datetime

class Alergi(db.Model):
    __tablename__ = 'alergi'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama_alergi = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nama_alergi': self.nama_alergi
        }
