from flask import Blueprint, render_template, request
from app.auth.utils import admin_login_required

from app.services.chart_service import (
    get_dashboard_summary,
    get_new_users_per_week,
    get_global_posture_score_trend,
    get_user_trends,
    get_user_calorie_trend,
)

from models.users import Users
from models.user_health import UserHealth
from models.posture_scan import PostureScan   # ← INI KUNCI
from models.recomendation import Recommendations
from config import db


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# =====================================================
# ========== DASHBOARD ================================
# =====================================================

@admin_bp.route("/dashboard")
@admin_login_required
def dashboard():
    summary = get_dashboard_summary()
    new_users = get_new_users_per_week()
    posture_scores = get_global_posture_score_trend()

    return render_template(
        "admin/dashboard.html",
        summary=summary,
        new_users=new_users,
        posture_scores=posture_scores,
    )

# =====================================================
# ========== USERS LIST ===============================
# =====================================================

@admin_bp.route("/users")
@admin_login_required
def users():
    q = request.args.get("q", "")
    posture = request.args.get("posture", "")

    query = Users.query

    # Search by name or email
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Users.name.ilike(like)) | (Users.email.ilike(like))
        )

    # Filter by posture category (HANYA JIKA FIELD INI ADA DI USER)
    if posture and hasattr(Users, "posture_category"):
        query = query.filter(Users.posture_category == posture)

    users = Users.query.order_by(Users.id.asc()).all()
    return render_template(
        "admin/users.html",
        users=users,
        q=q,
        posture=posture,
    )

# =====================================================
# ========== USER DETAIL ==============================
# =====================================================



@admin_bp.route("/users/<int:user_id>")
@admin_login_required
def user_detail(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return "User not found", 404

    # Ambil data kesehatan terakhir
    health = (
        UserHealth.query
        .filter_by(user_id=user.id)
        .order_by(UserHealth.created_at.desc())
        .first()
    )

    # Ambil posture scan terakhir (PAKAI CLASS, BUKAN MODULE)
    latest_posture = (
        PostureScan.query
        .filter_by(user_id=user.id)
        .order_by(PostureScan.created_at.desc())
        .first()
    )

    # Hitung total scan
    scan_count = (
        PostureScan.query
        .filter_by(user_id=user.id)
        .count()
    )

    return render_template(
        "admin/user_detail.html",
        user=user,
        health=health,
        posture=latest_posture,
        scan_count=scan_count,
    )


# =====================================================
# ========== POSTURE HISTORY ==========================
# =====================================================

@admin_bp.route("/users/<int:user_id>/posture")
@admin_login_required
def posture_history(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return "User not found", 404

    postures = (
        UserHealth.query
        .filter_by(user_id=user_id)
        .order_by(UserHealth.created_at.desc())
        .all()
    )

    return render_template(
        "admin/posture_history.html",
        user=user,
        postures=postures,
    )

# =====================================================
# ========== DIET HISTORY =============================
# =====================================================

@admin_bp.route("/users/<int:user_id>/diet")
@admin_login_required
def diet_history(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return "User not found", 404

    diets = (
        Recommendations.query
        .filter_by(user_id=user_id)
        .order_by(Recommendations.created_at.desc())
        .all()
    )

    calorie_trend = get_user_calorie_trend(user_id)

    return render_template(
        "admin/diet_history.html",
        user=user,
        diets=diets,
        calorie_trend=calorie_trend,
    )
