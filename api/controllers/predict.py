import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5)

def get_landmarks(img_path):
    img = cv2.imread(img_path)
    if img is None: return None
    h, w, _ = img.shape
    
    # Konversi BGR ke RGB untuk MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pose.process(img_rgb)
    
    if not result.pose_landmarks: return None
    lm = result.pose_landmarks.landmark

    # key_points = [11, 12, 23, 24, 25, 26] 
    # for point in key_points:
    #     if lm[point].visibility < 0.5: # Jika titik tidak terlihat jelas
    #         return "NOT_FULL_BODY"

    # Kembalikan koordinat dalam piksel asli sesuai ukuran gambar user
    return {
        "bahu_kiri": {"x": lm[11].x * w, "y": lm[11].y * h},
        "bahu_kanan": {"x": lm[12].x * w, "y": lm[12].y * h},
        "siku_kiri": {"x": lm[13].x * w, "y": lm[13].y * h},
        "siku_kanan": {"x": lm[14].x * w, "y": lm[14].y * h},
        "pinggang_kiri": {"x": lm[23].x * w, "y": lm[23].y * h},
        "pinggang_kanan": {"x": lm[24].x * w, "y": lm[24].y * h},
        "lutut_kiri": {"x": lm[25].x * w, "y": lm[25].y * h},
        "lutut_kanan": {"x": lm[26].x * w, "y": lm[26].y * h}
    }

def get_body_boxes(lm):
    # Menggunakan margin dinamis (5% dari tinggi badan) agar kotak tidak terlalu sempit
    tinggi_badan_px = abs(lm['lutut_kanan']['y'] - lm['bahu_kanan']['y'])
    margin = tinggi_badan_px * 0.05

    perut = [
        min(lm['pinggang_kanan']['x'], lm['pinggang_kiri']['x']) - margin,
        min(lm['bahu_kanan']['y'], lm['bahu_kiri']['y']) + (tinggi_badan_px * 0.3), # Mulai dari bawah dada
        max(lm['pinggang_kanan']['x'], lm['pinggang_kiri']['x']) + margin,
        lm['pinggang_kanan']['y'] + margin
    ]
    
    lengan = [
        min(lm['bahu_kanan']['x'], lm['siku_kanan']['x']) - margin,
        lm['bahu_kanan']['y'],
        max(lm['bahu_kanan']['x'], lm['siku_kanan']['x']) + margin,
        lm['siku_kanan']['y']
    ]
    
    paha = [
        min(lm['pinggang_kanan']['x'], lm['lutut_kanan']['x']) - margin,
        lm['pinggang_kanan']['y'],
        max(lm['pinggang_kanan']['x'], lm['lutut_kanan']['x']) + margin,
        lm['lutut_kanan']['y']
    ]
    
    return {"perut": perut, "lengan": lengan, "paha": paha}

def calculate_iou(boxA, boxB):
    xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
    xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0: return 0
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)

def scale_ideal_to_user(box_ideal, lm_ideal, lm_user):
    # Mencari skala berdasarkan tinggi torso (bahu ke lutut)
    t_ideal = abs(lm_ideal['lutut_kanan']['y'] - lm_ideal['bahu_kanan']['y'])
    t_user = abs(lm_user['lutut_kanan']['y'] - lm_user['bahu_kanan']['y'])
    skala = t_user / t_ideal
    
    w_id = (box_ideal[2] - box_ideal[0]) * skala
    h_id = (box_ideal[3] - box_ideal[1]) * skala
    
    # Penempatan kotak ideal di tengah-tengah pinggang user
    cx_u = (lm_user['pinggang_kiri']['x'] + lm_user['pinggang_kanan']['x']) / 2
    cy_u = (lm_user['pinggang_kiri']['y'] + lm_user['pinggang_kanan']['y']) / 2
    
    return [cx_u - w_id/2, cy_u - h_id/2, cx_u + w_id/2, cy_u + h_id/2]
