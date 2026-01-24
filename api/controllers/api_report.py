from flask import jsonify
from sqlalchemy import func
from models.posture_scan import PostureScan
from models.user_health import UserHealth
from config import db
from flask_jwt_extended import get_jwt_identity


def get_report():
    try:
        user_id = get_jwt_identity()
        health_data = UserHealth.query.filter_by(user_id=user_id)\
            .order_by(UserHealth.created_at.asc()).limit(7).all()
        
        # 2. Hitung ringkasan status perut (contoh statistik)
        # Menghitung berapa kali user mendapat status tertentu di tabel posture_scans
        stats = db.session.query(PostureScan.perut_status, func.count(PostureScan.perut_status))\
            .filter(PostureScan.user_id == user_id)\
            .group_by(PostureScan.perut_status).all()

        report_data = {
            "weight_trend": [
                {
                    "bulan": h.created_at.strftime('%b'), 
                    "berat": h.berat_badan
                } for h in health_data
            ],
            "posture_stats": {status: count for status, count in stats}
        }
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
