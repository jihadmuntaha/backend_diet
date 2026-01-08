from datetime import datetime, timedelta
from sqlalchemy import func
from config import db
from models.users import Users as User
from models.user_health import UserHealth
from models.recomendation import Recommendations
from models.posture_scan import PostureScan
from app.services.posture_service import classify_bmi

def get_dashboard_summary():
    total_users = db.session.query(func.count(User.id)).scalar() or 0

    avg_bmi = db.session.query(func.avg(UserHealth.bmi)).scalar()
    avg_bmi = round(avg_bmi, 2) if avg_bmi else None

    # posture_categories = {
    #     PostureScan.lengan_angle,
    #     PostureScan.lengan_status,
    #     PostureScan.paha_angle,
    #     PostureScan.paha_status,
    #     PostureScan.perut_angle,
    #     PostureScan.perut_status,
    # }
    # posture distribution
    posture_counts = (
        db.session.query(PostureScan.posture_overall, func.count(User.id))
        .group_by(PostureScan.posture_overall)
        .all()
    )
    posture_dist = {pc or "unknown": cnt for pc, cnt in posture_counts}

    # BMI category counts
    bmi = UserHealth.query.all()
    overweight = sum(1 for u in bmi if classify_bmi(u.bmi) == "overweight")
    ideal = sum(1 for u in bmi if classify_bmi(u.bmi) == "ideal")
    underweight = sum(1 for u in bmi if classify_bmi(u.bmi) == "underweight")

    # # posture bermasalah (kyphosis, lordosis, scoliosis)
    # problematic_postures = ("kyphosis", "lordosis", "scoliosis")
    # problematic_count = (
    #     db.session.query(func.count(User.id))
    #     .filter(User.posture_category.in_(problematic_postures))
    #     .scalar() or 0
    # )

    return {
        "total_users": total_users,
        "avg_bmi": avg_bmi,
        "posture_distribution": posture_dist,
        "overweight_count": overweight,
        "ideal_count": ideal,
        "underweight_count": underweight,
        # "problematic_posture_count": problematic_count,
    }

def get_new_users_per_week(weeks: int = 8):
    # 8 minggu terakhir
    now = datetime.utcnow()
    start = now - timedelta(weeks=weeks)

    rows = (
        db.session.query(
            func.yearweek(User.created_at), func.count(User.id)
        )
        .filter(User.created_at >= start)
        .group_by(func.yearweek(User.created_at))
        .order_by(func.yearweek(User.created_at))
        .all()
    )

    labels = []
    counts = []
    for yw, cnt in rows:
        labels.append(str(yw))
        counts.append(cnt)

    return {"labels": labels, "counts": counts}

def get_global_posture_score_trend(weeks: int = 8):
    now = datetime.utcnow()
    start = now - timedelta(weeks=weeks)

    rows = (
        db.session.query(
            func.date(PostureScan.created_at),
            func.avg(PostureScan.posture_overall),
        )
        .filter(PostureScan.created_at >= start)
        .group_by(func.date(PostureScan.created_at))
        .order_by(func.date(PostureScan.created_at))
        .all()
    )

    labels = [str(d) for d, _ in rows]
    scores = [round(s, 2) if s else None for _, s in rows]
    return {"labels": labels, "scores": scores}

def get_user_trends(user_id: int):
    # weight + BMI + posture score trend
    postures = (
        UserHealth.query
        .filter_by(user_id=user_id).join(PostureScan, PostureScan.user_health_id == UserHealth.id)
        .order_by(UserHealth.created_at.asc())
        .all()
    )

    dates = [p.created_at.date().isoformat() for p in postures]
    weights = [p.berat_badan for p in postures]
    bmis = [p.bmi for p in postures]
    overall = [p.posture_overall for p in postures]

    return {
        "dates": dates,
        "weights": weights,
        "bmis": bmis,
        "posture_overall": overall,
    }

def get_user_calorie_trend(user_id: int):
    diets = (
        Recommendations.query
        .filter_by(user_id=user_id)
        .order_by(Recommendations.record_date.asc())
        .all()
    )
    dates = [d.record_date.isoformat() for d in diets]
    intake = [d.calorie_intake for d in diets]
    targets = [d.daily_calorie_target for d in diets]
    return {"dates": dates, "intake": intake, "targets": targets}
