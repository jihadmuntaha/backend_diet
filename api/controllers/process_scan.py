import os
import json
from datetime import datetime
from api.controllers.api_recommendation import get_combined_recommendation
from config import db
from models.user_health import UserHealth
from models.posture_scan import PostureScan
from models.recomendation import Recommendations
from models.alergi import Alergi
from api.controllers.predict import get_landmarks, get_body_boxes, scale_ideal_to_user, calculate_iou

def tentukan_final(bagian_tubuh, hasil_sisi):
    # Ambil status dari 3 sisi
    st_depan = hasil_sisi['depan'][bagian_tubuh]['status']
    st_kanan = hasil_sisi['samping_kanan'][bagian_tubuh]['status']
    st_kiri = hasil_sisi['samping_kiri'][bagian_tubuh]['status']
    
    # Ambil rata-rata IoU untuk mengisi kolom 'angle'
    avg_iou = (hasil_sisi['depan'][bagian_tubuh]['iou'] + 
                hasil_sisi['samping_kanan'][bagian_tubuh]['iou'] + 
                hasil_sisi['samping_kiri'][bagian_tubuh]['iou']) / 3
        
    # Logika: Jika salah satu sisi Overweight, maka status akhir Overweight
    status_list = [st_depan, st_kanan, st_kiri]
    if "OVERWEIGHT" in status_list:
        final_status = "OVERWEIGHT"
    elif "UNDERWEIGHT" in status_list:
        final_status = "UNDERWEIGHT"
    else:
        final_status = "IDEAL"
            
    return final_status, round(avg_iou, 2)

def process_posture_scan(user_id, gender, tinggi, berat, files, db_ideal):
    # 1. Hitung BMI & Simpan Kesehatan
    tinggi_m = tinggi / 100
    bmi_value = berat / (tinggi_m ** 2)
    
    # Menentukan kategori BMI untuk 'posture_overall'
    if bmi_value < 18.5: st_bmi = "UNDERWEIGHT"
    elif 18.5 <= bmi_value < 25: st_bmi = "IDEAL"
    else: st_bmi = "OVERWEIGHT"

    health = UserHealth(
        user_id=user_id,
        tinggi_badan=tinggi,
        berat_badan=berat,
        bmi=bmi_value,
        created_at=datetime.utcnow()
    )
    db.session.add(health)

    # 2. Proses Foto per Sisi
    sisi_list = ['depan', 'samping_kanan', 'samping_kiri']
    hasil_sisi = {}

    for sisi in sisi_list:
        file = files.get(sisi)
        if not file: continue

        temp_path = f"temp_{sisi}_{user_id}.jpg"
        file.save(temp_path)
        
        lm_user = get_landmarks(temp_path)
        # if lm_user == "NOT_FULL_BODY":
        #     return {
        #         "status": "error",
        #         "message": f"Foto {sisi} hanya memperlihatkan sebagian tubuh. Pastikan seluruh tubuh dari kepala hingga lutut terlihat di kamera."
        #     }
        if lm_user:
            lm_ideal = db_ideal[f"{gender}_{sisi}"]
            u_boxes = get_body_boxes(lm_user)
            i_boxes_raw = get_body_boxes(lm_ideal)
            
            sisi_res = {}
            for bag in ['perut', 'lengan', 'paha']:
                box_u = u_boxes[bag]
                # Skalakan kotak ideal ke dimensi user untuk menghitung IoU (sebagai info saja)
                box_i_scaled = scale_ideal_to_user(i_boxes_raw[bag], lm_ideal, lm_user)
                iou = calculate_iou(box_u, box_i_scaled)
                
                # --- LOGIKA RASIO (Kunci Akurasi) ---
                # Hitung lebar relatif terhadap tinggi box tersebut
                w_u = box_u[2] - box_u[0]
                h_u = box_u[3] - box_u[1]
                ratio_user = w_u / h_u if h_u > 0 else 0

                w_i = box_i_scaled[2] - box_i_scaled[0]
                h_i = box_i_scaled[3] - box_i_scaled[1]
                ratio_ideal = w_i / h_i if h_i > 0 else 0

                # Threshold: 15% lebih lebar = Overweight, 15% lebih tipis = Underweight
                threshold = 0.15 
                
                if ratio_user > ratio_ideal * (1 + threshold):
                    status = "OVERWEIGHT"
                elif ratio_user < ratio_ideal * (1 - threshold):
                    status = "UNDERWEIGHT"
                else:
                    status = "IDEAL"
                
                sisi_res[bag] = {"status": status, "iou": round(iou, 2)}
            
            hasil_sisi[sisi] = sisi_res
        
        if os.path.exists(temp_path): os.remove(temp_path)
    # Validasi semua sisi terdeteksi
    required_sides = ['depan', 'samping_kanan', 'samping_kiri']
    missing_sides = [side for side in required_sides if side not in hasil_sisi]
    
    if missing_sides:
            mapping_nama = {
                'depan': 'Tampak Depan',
                'samping_kanan': 'Tampak Samping Kanan',
                'samping_kiri': 'Tampak Samping Kiri'
            }
            pesan_error = ", ".join([mapping_nama[s] for s in missing_sides])
            
            return {
                "status": "error",
                "message": f"Foto {pesan_error} tidak terdeteksi. Pastikan posisi berdiri tegak, seluruh tubuh terlihat, dan pencahayaan terang."
            }

    # Hitung nilai final untuk setiap bagian
    perut_stat, perut_iou = tentukan_final('perut', hasil_sisi)
    lengan_stat, lengan_iou = tentukan_final('lengan', hasil_sisi)
    paha_stat, paha_iou = tentukan_final('paha', hasil_sisi)

    # 3. Simpan Hasil Scan ke Database (Tabel posture_scans)
    new_scan = PostureScan(
        user_id=user_id,
        posture_overall=st_bmi, 
        perut_status=perut_stat,
        perut_angle=perut_iou,
        lengan_status=lengan_stat,
        lengan_angle=lengan_iou,
        paha_status=paha_stat,
        paha_angle=paha_iou,
        created_at=datetime.utcnow()
    )
    db.session.add(new_scan)
    db.session.flush() 

# --- (Bagian 4: Generate Rekomendasi) ---
    user_alergi = Alergi.query.filter_by(user_id=user_id).all()
    alergi_names = [a.nama_alergi for a in user_alergi]
    
    status_final_dict = {'perut': perut_stat, 'lengan': lengan_stat, 'paha': paha_stat}
    
    # Ambil hasil dari fungsi Excel
    res = get_combined_recommendation(status_final_dict, bmi_value, alergi_names)

    # SIMPAN KE DATABASE SEBAGAI STRING JSON
    new_recom = Recommendations(
        user_id=user_id,
        scan_id=new_scan.id,
        rekomendasi_makanan=json.dumps(res["makanan"]), # PENTING: dump ke string
        rekomendasi_olahraga=json.dumps(res["olahraga"]),
        created_at=datetime.utcnow()
    )
    db.session.add(new_recom)
    db.session.commit()

    return {
        "user_id": user_id,
        "bmi": round(bmi_value, 2),
        "posture": status_final_dict,
        "rekomendasi": {
            "makanan": res["makanan"], 
            "olahraga": res["olahraga"]
        }
    }