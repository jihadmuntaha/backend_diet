from flask import jsonify
from models.posture_scan import PostureScan
from flask_jwt_extended import get_jwt_identity

def get_history():
    try:
        user_id = get_jwt_identity() 
        
        # Query data hanya milik user yang sedang login
        scans = PostureScan.query.filter_by(user_id=user_id).order_by(PostureScan.created_at.desc()).all()
        
        # Mapping Hari & Bulan
        hari_indo = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        bulan_indo = {
            'January': 'Januari', 'February': 'Februari', 'March': 'Maret', 'April': 'April',
            'May': 'Mei', 'June': 'Juni', 'July': 'Juli', 'August': 'Agustus',
            'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Desember'
        }

        results = []
        for s in scans:
            if s.created_at:
                day_en = s.created_at.strftime('%A')
                month_en = s.created_at.strftime('%B')
                
                results.append({
                    "id": s.id, # Tambahan: id scan biasanya berguna untuk frontend
                    "hari": hari_indo.get(day_en, day_en),
                    "tanggal": s.created_at.strftime('%d'),
                    "bulan": bulan_indo.get(month_en, month_en),
                    "tahun": s.created_at.strftime('%Y'),
                    "lengan": s.lengan_status,
                    "perut": s.perut_status,
                    "paha": s.paha_status
                })
        
        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500