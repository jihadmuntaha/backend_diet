from flask import Blueprint, jsonify, request, g
from config import db
from models.users import Users as User
from app.auth.utils import auth_required, admin_required

user_bp = Blueprint("user", __name__, url_prefix="/api/users")

@user_bp.route("/me", methods=["GET"])
@auth_required
def get_me():
    return jsonify(g.current_user.to_dict())

@user_bp.route("/me", methods=["PUT"])
@auth_required
def update_me():
    user = g.current_user
    data = request.get_json() or {}

    for field in [
        "name",
        "height_cm",
        "weight_kg",
        "activity_level",
        "target_weight",
        "diet_type",
    ]:
        if field in data:
            setattr(user, field, data[field])

    if "allergies" in data:
        # terima bisa JSON list atau string
        user.allergies = data["allergies"]

    db.session.commit()
    return jsonify(user.to_dict())

# Admin: list users
@user_bp.route("/", methods=["GET"])
@admin_required
def list_users():
    q = request.args.get("q", "")
    posture = request.args.get("posture", "")

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.name.ilike(like)) | (User.email.ilike(like))
        )
    if posture:
        query = query.filter(User.posture_category == posture)

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])

@user_bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict())

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
