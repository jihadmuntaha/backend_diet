from datetime import datetime
from flask import request, jsonify
from api.controllers.process_scan import process_posture_scan
import json
from models.alergi import Alergi
from config import db

path_dataset = 'dataset/dataset_ideal.json'

def api_scan():
    user_id = request.form.get('id')
    tinggi = float(request.form.get('tinggi'))
    berat = float(request.form.get('berat'))
    alergi = request.form.getlist('alergi')
    gender = request.form.get('gender')
    
    files_data = {
        'depan': request.files.get('foto_depan'),
        'samping_kanan': request.files.get('foto_kanan'), 
        'samping_kiri': request.files.get('foto_kiri')  
    }

    for nama in alergi:
            existing_alergi = Alergi.query.filter_by(user_id=user_id, nama_alergi=nama).first()
            
            if not existing_alergi:
                baru = Alergi(
                    user_id=user_id, 
                    nama_alergi=nama,
                    created_at=datetime.utcnow()
                )
                db.session.add(baru)
        
    db.session.commit()

    try:
        with open(path_dataset, 'r') as f:
            db_ideal = json.load(f)
            
        hasil = process_posture_scan(user_id, gender, tinggi, berat, files_data, db_ideal)
        
        if isinstance(hasil, dict) and hasil.get("status") == "error":
            return jsonify(hasil), 400 
        print(hasil)
        return jsonify({"status": "success", "data": hasil}), 200

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": f"Terjadi kesalahan sistem: {str(e)}"}), 500
