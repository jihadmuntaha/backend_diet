import datetime
import json
from flask import jsonify, request
import pandas as pd
from config import db
from models.recomendation import Recommendations
from flask_jwt_extended import get_jwt_identity as jwt


import datetime
import json
import pandas as pd

def get_combined_recommendation(status_dict, bmi, alergi_list):
    # Sesuaikan path jika perlu
    df_menu = pd.read_excel('dataset/dataset_kesehatan_lengkap.xlsx', sheet_name='Master_Menu')
    df_jadwal = pd.read_excel('dataset/dataset_kesehatan_lengkap.xlsx', sheet_name='Jadwal_Harian')
    df_olahraga = pd.read_excel('dataset/dataset_kesehatan_lengkap.xlsx', sheet_name='Master_Olahraga')

    hari_indo = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}[datetime.datetime.now().weekday()]
    
    # 1. LOGIKA MAKANAN
    is_any_overweight = any(s == "OVERWEIGHT" for s in status_dict.values())
    
    if is_any_overweight:
        col_target = 'ID_OVERWEIGHT'
    elif bmi < 18.5:
        col_target = 'ID_UNDERWEIGHT'
    else:
        col_target = 'ID_IDEAL'

    jadwal_rows = df_jadwal[df_jadwal['Hari'] == hari_indo]
    makanan_result = []
    
    for _, row in jadwal_rows.iterrows():
        id_menu = row[col_target]
        menu_info = df_menu[df_menu['ID_Menu'] == id_menu].iloc[0]
        
        # LOGIKA ALERGI: Jika bahan mengandung kata kunci alergi
        bahan = str(menu_info['Bahan_Kunci']).lower()
        nama_final = menu_info['Nama_Menu']
        
        # Cek apakah ada alergi user di dalam bahan makanan
        if any(a.lower().strip() in bahan for a in alergi_list):
            # Ambil menu cadangan (Ideal) jika menu utama mengandung alergi
            id_alt = row['ID_IDEAL']
            menu_alt = df_menu[df_menu['ID_Menu'] == id_alt].iloc[0]
            nama_final = f"{menu_alt['Nama_Menu']} (Alt Alergi)"

        makanan_result.append({
            "waktu": row['Waktu'],
            "nama": nama_final,
            "jam": row['Rentang_Jam']
        })

    # 2. LOGIKA OLAHRAGA
    olahraga_result = []
    for area, status in status_dict.items():
        if status != "IDEAL":
            match = df_olahraga[(df_olahraga['Fokus_Area'] == area.capitalize()) & (df_olahraga['Status'] == status)]
            if not match.empty:
                row_o = match.iloc[0]
                olahraga_result.append({
                    "area": area.capitalize(),
                    "gerakan": row_o['Nama_Gerakan'],
                    "durasi": row_o['Repetisi_Durasi'],
                    "jam": row_o['Rentang_Jam']
                })
            
    return {"makanan": makanan_result, "olahraga": olahraga_result}

def api_get_recommendation():
    try:
        data = request.json
        user_id = data.get('user_id')
        scan_id = data.get('scan_id') # Ambil ID scan yang baru saja dilakukan
        bmi = data.get('bmi')
        status_dict = data.get('posture')
        alergi = data.get('alergi', [])

        # 1. Jalankan fungsi logika dari Excel
        result = get_combined_recommendation(status_dict, bmi, alergi)

        if result is None:
            return jsonify({"status": "error", "message": "Dataset error"}), 500

        # 2. SIMPAN KE DATABASE (Tabel Recommendations)
        # Kita ubah list/dict menjadi String JSON agar masuk ke kolom Text database
        new_recom = Recommendations(
            user_id=user_id,
            scan_id=scan_id,
            rekomendasi_makanan=json.dumps(result["makanan"]), # Simpan sebagai string JSON
            rekomendasi_olahraga=json.dumps(result["olahraga"]),
            created_at=datetime.utcnow()
        )
        db.session.add(new_recom)
        db.session.commit() # Database menyimpan data secara permanen

        # 3. Balas ke Flutter
        return jsonify({
            "status": "success",
            "recom_id": new_recom.id, # Kirim ID rekomendasinya juga
            "data": {
                "makanan": result["makanan"],
                "olahraga": result["olahraga"]
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
    
def get_latest_recommendation():
    try:
        user_id = jwt()
        # Ambil rekomendasi terbaru milik user ini
        recom = Recommendations.query.filter_by(user_id=user_id).order_by(Recommendations.created_at.desc()).first()
        
        if not recom:
            return jsonify({"status": "error", "message": "Belum ada riwayat scan"}), 404

        return jsonify({
            "status": "success",
            "data": {
                "makanan": json.loads(recom.rekomendasi_makanan),
                "olahraga": json.loads(recom.rekomendasi_olahraga)
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500    