import os
import json
from datetime import datetime
from config import db
from models.user_health import UserHealth
from models.postur_scan import PostureScan
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
        if not file:
            continue

        temp_path = f"temp_{sisi}_{user_id}.jpg"
        file.save(temp_path)
        
        lm_user = get_landmarks(temp_path)
        try: 
            if lm_user:
                print(f"DEBUG: Berhasil deteksi landmark untuk {sisi}")
                lm_ideal = db_ideal[f"{gender}_{sisi}"]
                u_boxes = get_body_boxes(lm_user)
                i_boxes_raw = get_body_boxes(lm_ideal)
                
                sisi_res = {}
                for bag in ['perut', 'lengan', 'paha']:
                    box_u = u_boxes[bag]
                    box_i_scaled = scale_ideal_to_user(i_boxes_raw[bag], lm_ideal, lm_user)
                    iou = calculate_iou(box_u, box_i_scaled)
                    
                    luas_u = (box_u[2]-box_u[0]) * (box_u[3]-box_u[1])
                    luas_i = (box_i_scaled[2]-box_i_scaled[0]) * (box_i_scaled[3]-box_i_scaled[1])
                    
                    status = "IDEAL" if iou > 0.75 else ("OVERWEIGHT" if luas_u > luas_i else "UNDERWEIGHT")
                    sisi_res[bag] = {"status": status, "iou": round(iou, 2)}
                
                hasil_sisi[sisi] = sisi_res
            else:
                print(f"DEBUG: Gagal deteksi landmark untuk {sisi}")
        except Exception as e:
            print(f"Error proses {sisi}: {e}")
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

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

    # 4. Generate Rekomendasi
    user_alergi = Alergi.query.filter_by(user_id=user_id).all()
    alergi_names = [a.nama_alergi for a in user_alergi]
    
    # Kirim status final ke logika diet
    status_final_dict = {
        'perut': perut_stat,
        'lengan': lengan_stat,
        'paha': paha_stat
    }
    
    rekom_makanan, rekom_olahraga = generate_diet_logic(status_final_dict, bmi_value, alergi_names)

    new_recom = Recommendations(
        user_id=user_id,
        scan_id=new_scan.id,
        rekomendasi_makanan=rekom_makanan,
        rekomendasi_olahraga=rekom_olahraga,
        created_at=datetime.utcnow()
    )
    db.session.add(new_recom)
    db.session.commit()

    return {
        "bmi": round(bmi_value, 2),
        "posture": status_final_dict,
        "rekomendasi": {"makanan": rekom_makanan, "olahraga": rekom_olahraga}
    }

def generate_diet_logic(status_final, bmi, alergi):
    makanan = "Konsumsi protein seimbang dan sayuran."
    olahraga = "Lakukan aktivitas fisik ringan seperti jalan kaki."
    
    # Contoh logika: Jika perut Overweight
    if status_final['perut'] == "OVERWEIGHT" or bmi > 25:
        makanan = "Kurangi asupan karbohidrat dan gula, lakukan defisit kalori."
        olahraga = "Fokus pada olahraga kardio dan plank untuk mengecilkan perut."
        
    # Logika Alergi
    alergi_lower = [a.lower() for a in alergi]
    if "babi" in alergi_lower:
        makanan += " Pilih sumber protein halal seperti ayam, sapi, atau ikan."
    if "udang" in alergi_lower or "seafood" in alergi_lower:
        makanan += " Ganti sumber protein laut dengan protein nabati seperti tempe."
        
    return makanan, olahraga