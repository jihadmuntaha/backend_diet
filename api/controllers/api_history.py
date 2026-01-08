from flask import jsonify
from models.posture_scan import PostureScan


def get_history(user_id):
    try:
        scans = PostureScan.query.filter_by(user_id=user_id).order_by(PostureScan.created_at.desc()).all()

        hari_indo = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        
        # Mapping Bulan
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
                    "hari": hari_indo.get(day_en, day_en),
                    "tanggal": s.created_at.strftime('%d'),
                    "bulan": bulan_indo.get(month_en, month_en),
                    "tahun": s.created_at.strftime('%Y'),
                    "lengan": s.lengan_status,
                    "perut": s.perut_status,
                    "paha": s.paha_status
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
