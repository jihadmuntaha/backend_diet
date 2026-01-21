from models.user_reviews import UserReview
from config import db
from sqlalchemy import func

def get_review_statistics():
    """
    Mengambil statistik review untuk dashboard
    """
    # Hitung rata-rata
    avg_rating = db.session.query(func.avg(UserReview.rating)).scalar() or 0
    
    # Hitung distribusi
    stats = db.session.query(
        UserReview.rating, 
        func.count(UserReview.id)
    ).group_by(UserReview.rating).all()
    
    dist_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating, count in stats:
        dist_dict[rating] = count
        
    return {
        "average_rating": round(float(avg_rating), 1),
        "distribution": dist_dict,
        "total_reviews": sum(dist_dict.values())
    }

def create_new_review(user_id, rating, comment, sentiment):
    """
    Logika menyimpan review baru
    """
    new_review = UserReview(
        user_id=user_id,
        rating=rating,
        sentiment=sentiment,
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()
    return new_review