import json
from typing import Dict, List
from models.users import Users as User
from models.user_health import UserHealth
from app.services.posture_service import classify_bmi

def estimate_calorie_target(
    bmi: float,
    activity_level: str,
    target_weight: float,
    current_weight: float,
    diet_type: str,
) -> float:
    """
    Rough estimation:
    - base from current weight * 30
    - adjust by activity level, diet type
    """
    if current_weight is None:
        return None

    base = current_weight * 30  # kkal

    act = (activity_level or "").lower()
    if act == "sedentary":
        base *= 0.9
    elif act == "light":
        base *= 1.0
    elif act == "moderate":
        base *= 1.1
    elif act == "heavy":
        base *= 1.25

    dt = (diet_type or "").lower()
    if dt == "cutting":
        base -= 300
    elif dt == "bulking":
        base += 300

    base = max(1200, base)
    return round(base, 0)

def filter_foods_by_allergy(allergies: List[str]) -> List[str]:
    """
    Dummy recommended foods list.
    Real case: pull from DB.
    """
    base_foods = [
        "ayam panggang",
        "ikan tuna",
        "telur rebus",
        "oatmeal",
        "nasi merah",
        "brokoli",
        "alpukat",
        "tahu",
        "tempe",
        "susu sapi",
        "kacang tanah",
    ]

    allergies_lower = [a.strip().lower() for a in allergies or []]

    filtered = []
    for food in base_foods:
        f = food.lower()
        if "susu" in f and ("milk" in allergies_lower or "susu" in allergies_lower or "dairy" in allergies_lower):
            continue
        if "telur" in f and ("egg" in allergies_lower or "telur" in allergies_lower):
            continue
        if "kacang" in f and ("peanut" in allergies_lower or "kacang" in allergies_lower):
            continue
        filtered.append(food)

    return filtered

def build_posture_exercises(posture_category: str) -> List[str]:
    posture_category = (posture_category or "").lower()
    if posture_category == "kyphosis":
        return ["thoracic extension", "wall angels", "scapular retraction"]
    elif posture_category == "lordosis":
        return ["hamstring stretch", "plank", "pelvic tilt"]
    elif posture_category == "scoliosis":
        return ["side plank", "cat-cow stretch", "latissimus dorsi stretch"]
    else:
        return ["plank", "glute bridge", "bird-dog"]

def generate_diet_recommendation(
    user: User,
    latest_posture: UserHealth = None,
) -> Dict:
    allergies = []
    if user.allergies:
        try:
            allergies = json.loads(user.allergies)
        except Exception:
            # bisa juga: user.allergies comma separated
            allergies = [a.strip() for a in user.allergies.split(",")]

    bmi = user.bmi
    if bmi is None and user.height_cm and user.weight_kg:
        from app.services.posture_service import calculate_bmi
        bmi = calculate_bmi(user.height_cm, user.weight_kg)

    calorie_target = estimate_calorie_target(
        bmi=bmi,
        activity_level=user.activity_level,
        target_weight=user.target_weight,
        current_weight=user.weight_kg,
        diet_type=user.diet_type,
    )

    foods = filter_foods_by_allergy(allergies)
    posture_category = latest_posture.posture_category if latest_posture else user.posture_category
    exercises = build_posture_exercises(posture_category)

    return {
        "bmi": bmi,
        "bmi_category": classify_bmi(bmi),
        "daily_calorie_target": calorie_target,
        "recommended_foods": foods,
        "recommended_exercises": exercises,
    }
