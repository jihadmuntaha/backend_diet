from flask import Blueprint, render_template, jsonify, request, session
from app.auth.utils import admin_login_required

from app.services.chart_service import (
    get_dashboard_summary,
    get_new_users_per_week,
    get_global_posture_score_trend,
    get_user_trends,
    get_user_calorie_trend,
    
)

from config import db
from app.services.review_service import get_review_statistics
from models.users import Users
from models.user_health import UserHealth
from models.posture_scan import PostureScan   # ← INI KUNCI
from models.recomendation import Recommendations
from models.user_reviews import UserReview
from config import db
from sqlalchemy import text, func


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# =====================================================
# ========== DASHBOARD ================================
# =====================================================

@admin_bp.route("/dashboard")
@admin_login_required
def dashboard():
    summary = get_dashboard_summary()  # Pastikan fungsi ini mereturn dict
    new_users = get_new_users_per_week()
    posture_scores = get_global_posture_score_trend()
    
    # Ambil data statistik dari service
    review_stats = get_review_statistics()

    # PERBAIKAN: Masukkan nilai rata-rata ke key yang tepat di summary
    # Gunakan float() untuk memastikan tidak error saat render di template
    summary["avg_user_rating"] = float(review_stats["average_rating"])

    # Siapkan data grafik
    chart_review_data = [
        review_stats["distribution"][1],
        review_stats["distribution"][2],
        review_stats["distribution"][3],
        review_stats["distribution"][4],
        review_stats["distribution"][5]
    ]

    return render_template(
        "admin/dashboard.html",
        summary=summary,
        new_users=new_users,
        posture_scores=posture_scores,
        chart_review_data=chart_review_data
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



# ====================================================
# ========== USER REVIEW =============================
# =====================================================

@admin_bp.route("/reviews")
@admin_login_required
def view_reviews():
    # Gunakan join untuk mengambil data user sekaligus
    reviews = db.session.query(UserReview, Users.fullname).join(
        Users, UserReview.user_id == Users.id
    ).order_by(UserReview.created_at.desc()).all()
    
    # Kita modifikasi sedikit agar mudah dibaca di template
    formatted_reviews = []
    for r, fullname in reviews:
        review_dict = r.__dict__
        review_dict['user_name'] = fullname # Tambahkan nama ke dictionary
        formatted_reviews.append(review_dict)

    return render_template("admin/reviews.html", reviews=formatted_reviews)

# =====================================================
# ========== POSTURE HISTORY ==========================
# =====================================================

@admin_bp.route("/posture-history")
@admin_login_required
def posture_history_index():
    # Ambil user_id dari query string (misal: ?user_id=5)
    selected_user_id = request.args.get('user_id', type=int)
    
    # Ambil semua user (non-admin) untuk isi pilihan di dropdown
    all_users = Users.query.filter(Users.role != 'admin').order_by(Users.fullname).all()
    
    selected_user = None
    postures = []
    
    if selected_user_id:
        selected_user = db.session.get(Users, selected_user_id)
        if selected_user:
            postures = (
                PostureScan.query
                .filter_by(user_id=selected_user_id)
                .order_by(PostureScan.created_at.desc())
                .all()
            )

    return render_template(
        "admin/posture_history.html",
        all_users=all_users,
        selected_user=selected_user,
        postures=postures
    )

# =====================================================
# ========== DIET HISTORY =============================
# =====================================================

@admin_bp.route("/diet-history")
@admin_login_required
def diet_history_index():
    # Ambil user_id dari parameter URL (?user_id=...)
    selected_user_id = request.args.get('user_id', type=int)
    
    # Ambil daftar user non-admin untuk dropdown
    all_users = Users.query.filter(Users.role != 'admin').order_by(Users.fullname).all()
    
    selected_user = None
    diets = []
    
    if selected_user_id:
        selected_user = db.session.get(Users, selected_user_id)
        if selected_user:
            # Ambil history rekomendasi user tersebut
            diets = (
                Recommendations.query
                .filter_by(user_id=selected_user_id)
                .order_by(Recommendations.created_at.desc())
                .all()
            )

    return render_template(
        "admin/diet_history.html",
        all_users=all_users,
        selected_user=selected_user,
        diets=diets
    )   

    
# =====================================================
# ========== HEALTH ==============================    
# =====================================================

@admin_bp.route("/health", methods=["GET"])
def health():
    try:
        # Cek koneksi ke database
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "message": "Database connection successful"
        }), 200
    except Exception as e:
        # Tangani error koneksi
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.session.close()
