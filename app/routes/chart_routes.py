from flask import Blueprint, jsonify, g
from app.auth.utils import auth_required, admin_required
from app.services.chart_service import (
    get_user_trends,
    get_user_calorie_trend,
    get_dashboard_summary,
    get_new_users_per_week,
    get_global_posture_score_trend,
)

chart_bp = Blueprint("chart", __name__, url_prefix="/api/charts")

# Untuk mobile: trend user sendiri
@chart_bp.route("/me/posture", methods=["GET"])
@auth_required
def me_posture_trend():
    data = get_user_trends(g.current_user.id)
    return jsonify(data)

@chart_bp.route("/me/calorie", methods=["GET"])
@auth_required
def me_calorie_trend():
    data = get_user_calorie_trend(g.current_user.id)
    return jsonify(data)

# Untuk admin dashboard (bisa juga dipakai via AJAX di template)
@chart_bp.route("/admin/summary", methods=["GET"])
@admin_required
def admin_summary():
    return jsonify(get_dashboard_summary())

@chart_bp.route("/admin/new_users", methods=["GET"])
@admin_required
def admin_new_users():
    return jsonify(get_new_users_per_week())

@chart_bp.route("/admin/posture_scores", methods=["GET"])
@admin_required
def admin_posture_scores():
    return jsonify(get_global_posture_score_trend())
