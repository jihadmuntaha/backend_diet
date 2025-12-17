from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.posture import PostureMeasurement
from app.models.diet import DietRecord
from app.services.posture_service import classify_bmi

def get_dashboard_summary():
    total_users = db.session.query(func.count(User.id)).scalar() or 0

    avg_bmi = db.session.query(func.avg(User.bmi)).scalar()
    avg_bmi = round(avg_bmi, 2) if avg_bmi else None

    # posture distribution
    posture_counts = (
        db.session.query(User.posture_category, func.count(User.id))
        .group_by(User.posture_category)
        .all()
    )
    posture_dist = {pc or "unknown": cnt for pc, cnt in posture_counts}

    # BMI category counts
    users = User.query.all()
    obesity = sum(1 for u in users if classify_bmi(u.bmi) == "obesity")
    underweight = sum(1 for u in users if classify_bmi(u.bmi) == "underweight")

    # posture bermasalah (kyphosis, lordosis, scoliosis)
    problematic_postures = ("kyphosis", "lordosis", "scoliosis")
    problematic_count = (
        db.session.query(func.count(User.id))
        .filter(User.posture_category.in_(problematic_postures))
        .scalar() or 0
    )

    return {
        "total_users": total_users,
        "avg_bmi": avg_bmi,
        "posture_distribution": posture_dist,
        "obesity_count": obesity,
        "underweight_count": underweight,
        "problematic_posture_count": problematic_count,
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
            func.date(PostureMeasurement.created_at),
            func.avg(PostureMeasurement.posture_score),
        )
        .filter(PostureMeasurement.created_at >= start)
        .group_by(func.date(PostureMeasurement.created_at))
        .order_by(func.date(PostureMeasurement.created_at))
        .all()
    )

    labels = [str(d) for d, _ in rows]
    scores = [round(s, 2) if s else None for _, s in rows]
    return {"labels": labels, "scores": scores}

def get_user_trends(user_id: int):
    # weight + BMI + posture score trend
    postures = (
        PostureMeasurement.query
        .filter_by(user_id=user_id)
        .order_by(PostureMeasurement.created_at.asc())
        .all()
    )

    dates = [p.created_at.date().isoformat() for p in postures]
    weights = [p.weight_kg for p in postures]
    bmis = [p.bmi for p in postures]
    scores = [p.posture_score for p in postures]

    return {
        "dates": dates,
        "weights": weights,
        "bmis": bmis,
        "posture_scores": scores,
    }

def get_user_calorie_trend(user_id: int):
    diets = (
        DietRecord.query
        .filter_by(user_id=user_id)
        .order_by(DietRecord.record_date.asc())
        .all()
    )
    dates = [d.record_date.isoformat() for d in diets]
    intake = [d.calorie_intake for d in diets]
    targets = [d.daily_calorie_target for d in diets]
    return {"dates": dates, "intake": intake, "targets": targets}
