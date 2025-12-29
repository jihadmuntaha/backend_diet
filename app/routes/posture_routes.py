import json
from flask import Blueprint, request, jsonify, g
from config import db
from models.user_health import UserHealth
# from models.users import Users as User
from app.auth.utils import auth_required, admin_required
from app.services.posture_service import calculate_bmi, classify_posture_from_keypoints

posture_bp = Blueprint("posture", __name__, url_prefix="/api/posture")

@posture_bp.route("", methods=["POST"])
@auth_required
def create_posture_measurement():
    data = request.get_json() or {}

    height_cm = data.get("height_cm") or g.current_user.height_cm
    weight_kg = data.get("weight_kg") or g.current_user.weight_kg
    keypoints = data.get("keypoints")

    if not keypoints:
        return jsonify({"message": "keypoints is required"}), 400

    keypoints_str = keypoints if isinstance(keypoints, str) else json.dumps(keypoints)

    bmi = calculate_bmi(height_cm, weight_kg)
    posture_category, posture_score = classify_posture_from_keypoints(keypoints_str)

    posture = UserHealth(
        user_id=g.current_user.id,
        height_cm=height_cm,
        weight_kg=weight_kg,
        bmi=bmi,
    )

    db.session.add(posture)
    # update snapshot di user
    user = g.current_user
    user.height_cm = height_cm
    user.weight_kg = weight_kg
    user.bmi = bmi
    db.session.commit()

    return jsonify(posture.to_dict()), 201

@posture_bp.route("/history", methods=["GET"])
@auth_required
def my_posture_history():
    postures = (
        UserHealth.query
        .filter_by(user_id=g.current_user.id)
        .order_by(UserHealth.created_at.desc())
        .all()
    )
    return jsonify([p.to_dict() for p in postures])

# Admin: get user posture history
@posture_bp.route("/user/<int:user_id>", methods=["GET"])
@admin_required
def user_posture_history(user_id):
    postures = (
        UserHealth.query
        .filter_by(user_id=user_id)
        .order_by(UserHealth.created_at.desc())
        .all()
    )
    return jsonify([p.to_dict() for p in postures])
