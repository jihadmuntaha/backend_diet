import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

# proses menghitung IOU(intersection over Union) dari 2 bounding box
def calculate_iou(boxA, boxB):
    xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
    xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(boxAArea + boxBArea - interArea)

# fungsi untuk mendapatkan bounding box dari bagian tubuh tertentu
def get_body_boxes(lm):
    perut = [min(lm['bahu_kanan']['x'], lm['bahu_kiri']['x']),
             min(lm['bahu_kanan']['y'], lm['bahu_kiri']['y']),
             max(lm['pinggang_kanan']['x'], lm['pinggang_kiri']['x']),
             max(lm['pinggang_kanan']['y'], lm['pinggang_kiri']['y'])]
    lengan = [min(lm['bahu_kanan']['x'], lm['siku_kanan']['x']) - 15,
              min(lm['bahu_kanan']['y'], lm['siku_kanan']['y']),
              max(lm['bahu_kanan']['x'], lm['siku_kanan']['x']) + 15,
              max(lm['bahu_kanan']['y'], lm['siku_kanan']['y'])]
    paha = [min(lm['pinggang_kanan']['x'], lm['lutut_kanan']['x']) - 20,
            min(lm['pinggang_kanan']['y'], lm['lutut_kanan']['y']),
            max(lm['pinggang_kanan']['x'], lm['lutut_kanan']['x']) + 20,
            max(lm['pinggang_kanan']['y'], lm['lutut_kanan']['y'])]
    
    return {"perut": perut, "lengan": lengan, "paha": paha}

# fungsi untuk menskalakan bounding box ideal ke ukuran user
def scale_ideal_to_user(box_ideal, lm_ideal, lm_user):
    t_ideal = abs(lm_ideal['lutut_kanan']['y'] - lm_ideal['bahu_kanan']['y'])
    t_user = abs(lm_user['lutut_kanan']['y'] - lm_user['bahu_kanan']['y'])
    skala = t_user / t_ideal
    w_id = (box_ideal[2] - box_ideal[0]) * skala
    h_id = (box_ideal[3] - box_ideal[1]) * skala
    cx_u = (lm_user['pinggang_kiri']['x'] + lm_user['pinggang_kanan']['x']) / 2
    cy_u = (lm_user['pinggang_kiri']['y'] + lm_user['pinggang_kanan']['y']) / 2

    return [cx_u - w_id/2, cy_u - h_id/2, cx_u + w_id/2, cy_u + h_id/2]

# fungsi untuk mendapatkan landmark dari gambar
def get_landmarks(img_path):
    img = cv2.imread(img_path)
    if img is None: return None
    h, w, _ = img.shape
    resize = cv2.resize(img, (400, 400))
    result = pose.process(cv2.cvtColor(resize, cv2.COLOR_BGR2RGB))
    if not result.pose_landmarks: return None
    lm = result.pose_landmarks.landmark

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