import json
from datetime import date
from flask import Blueprint, request, jsonify, g
from app import db
from app.models.diet import DietRecord
from app.models.posture import PostureMeasurement
from app.auth.utils import auth_required, admin_required
from app.services.diet_service import generate_diet_recommendation

diet_bp = Blueprint("diet", __name__, url_prefix="/api/diet")

@diet_bp.route("/recommendation", methods=["POST"])
@auth_required
def create_recommendation_and_record():
    data = request.get_json() or {}
    calorie_intake = data.get("calorie_intake")

    latest_posture = (
        PostureMeasurement.query
        .filter_by(user_id=g.current_user.id)
        .order_by(PostureMeasurement.created_at.desc())
        .first()
    )

    rec = generate_diet_recommendation(g.current_user, latest_posture)

    record = DietRecord(
        user_id=g.current_user.id,
        record_date=date.today(),
        calorie_intake=calorie_intake,
        daily_calorie_target=rec["daily_calorie_target"],
        recommended_foods=json.dumps(rec["recommended_foods"]),
        recommended_exercises=json.dumps(rec["recommended_exercises"]),
        notes=data.get("notes"),
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
        DietRecord.query
        .filter_by(user_id=g.current_user.id)
        .order_by(DietRecord.record_date.desc())
        .all()
    )
    return jsonify([d.to_dict() for d in diets])

# Admin: diet history user tertentu
@diet_bp.route("/user/<int:user_id>", methods=["GET"])
@admin_required
def user_diet_history(user_id):
    diets = (
        DietRecord.query
        .filter_by(user_id=user_id)
        .order_by(DietRecord.record_date.desc())
        .all()
    )
    return jsonify([d.to_dict() for d in diets])
