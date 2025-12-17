import json
from typing import Dict, Tuple

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    if not height_cm or not weight_kg:
        return None
    height_m = height_cm / 100.0
    if height_m <= 0:
        return None
    return round(weight_kg / (height_m ** 2), 2)

def classify_bmi(bmi: float) -> str:
    if bmi is None:
        return "unknown"
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obesity"

def classify_posture_from_keypoints(keypoints_json: str) -> Tuple[str, float]:
    """
    Dummy rules dari Mediapipe keypoints.
    Misal:
    - jika kemiringan bahu > threshold -> 'kyphosis'
    - dll
    Di sini gw bikin dummy simple.
    """
    try:
        data = json.loads(keypoints_json)
    except Exception:
        return "unknown", 50.0

    score = 80.0
    category = "normal"

    shoulder_tilt = data.get("shoulder_tilt", 0.0)
    spine_curve = data.get("spine_curve", 0.0)
    pelvis_tilt = data.get("pelvis_tilt", 0.0)

    # Dummy thresholds
    if abs(spine_curve) > 0.4:
        category = "scoliosis"
        score -= 30
    elif shoulder_tilt > 0.3:
        category = "kyphosis"
        score -= 20
    elif pelvis_tilt > 0.3:
        category = "lordosis"
        score -= 20

    score = max(0.0, min(100.0, score))
    return category, score
