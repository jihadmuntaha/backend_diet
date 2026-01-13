from flask import Blueprint, request, jsonify, g
from config import db
from models.user_reviews import UserReview
from app.auth.utils import auth_required  # sesuai route auth lo

user_reviews_bp = Blueprint("user_reviews", __name__, url_prefix="/api/user_reviews")

# Tambah feedback
@user_reviews_bp.route("/", methods=["POST"])
@auth_required
def create_feedback():
    data = request.get_json()
    rating = data.get("rating")
    comment = data.get("comment", "")

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating harus 1-5"}), 400

    review = UserReview(user_id=g.current_user.id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Feedback berhasil dikirim", "review_id": review.id}), 201

# List semua feedback
@user_reviews_bp.route("/", methods=["GET"])
def get_feedbacks():
    reviews = UserReview.query.order_by(UserReview.created_at.desc()).all()
    result = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat()
        } for r in reviews
    ]
    return jsonify(result), 200