from flask import request, jsonify
from config import db
from models.users import Users as User
from flask_jwt_extended import get_jwt_identity

def handle_change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"status": False, "message": "Password lama dan baru harus diisi"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": False, "message": "User tidak ditemukan"}), 404

        # 1. Gunakan fungsi check_password yang ada di MODEL
        if not user.check_password(old_password):
            return jsonify({"status": False, "message": "Password lama salah"}), 401

        # 2. Gunakan fungsi set_password yang ada di MODEL
        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            "status": True,
            "message": "Password berhasil diperbarui"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": False, "message": str(e)}), 500