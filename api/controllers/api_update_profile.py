import os
from flask import jsonify, request, request
from models.users import Users as User
from config import db, app


def update_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        # Update teks (Nama & Email)
        user.fullname = request.form.get('fullname', user.fullname)
        user.email = request.form.get('email', user.email)

        # Handle Upload Foto
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_picture = filename # Simpan nama file ke kolom profile_picture

        db.session.commit()
        return jsonify({"message": "Update berhasil", "profile_picture": user.profile_picture})
    except Exception as e:
        return jsonify({"error": str(e)}), 500