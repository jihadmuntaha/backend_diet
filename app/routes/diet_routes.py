import json
from datetime import date
from flask import Blueprint, request, jsonify, g
from config import db
from models.recomendation import Recommendations
from models.user_health import UserHealth
from app.auth.utils import auth_required, admin_required
from app.services.diet_service import generate_diet_recommendation

diet_bp = Blueprint("diet", __name__, url_prefix="/api/diet")

@diet_bp.route("/recommendation", methods=["POST"])
@auth_required
def create_recommendation_and_record():
    data = request.get_json() or {}
    calorie_intake = data.get("calorie_intake")

    latest_posture = (
        UserHealth.query
        .filter_by(user_id=g.current_user.id)
        .order_by(UserHealth.created_at.desc())
        .first()
    )

    rec = generate_diet_recommendation(g.current_user, latest_posture)

    record = Recommendations(
        user_id=g.current_user.id,
        scan_id=data.get("scan_id"),
        rekomendasi_makanan=json.dumps(rec["recommended_foods"]),
        rekomendasi_olahraga=json.dumps(rec["recommended_exercises"]), 
    )

    db.session.add(record)
    db.session.commit()

    resp = record.to_dict()
    resp["recommendation"] = rec
    return jsonify(resp), 201

@diet_bp.route("/history", methods=["GET"])
@auth_required
def my_diet_history():
    diets = (
        Recommendations.query
        .filter_by(user_id=g.current_user.id)
        .order_by(Recommendations.record_date.desc())
        .all()
    )
    return jsonify([d.to_dict() for d in diets])

# Admin: diet history user tertentu
@diet_bp.route("/user/<int:user_id>", methods=["GET"])
@admin_required
def user_diet_history(user_id):
    diets = (
        Recommendations.query
        .filter_by(user_id=user_id)
        .order_by(Recommendations.record_date.desc())
        .all()
    )
    return jsonify([d.to_dict() for d in diets])
