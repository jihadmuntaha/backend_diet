import os
from flask import request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from config import db
from models.users import Users as User
from flask_jwt_extended import get_jwt_identity

def update_profile():
    user_id = get_jwt_identity()
    try:
        user = User.query.get(user_id)
        user.fullname = request.form.get('fullname', user.fullname)
        user.email = request.form.get('email', user.email)
        user.jenis_kelamin = request.form.get('jenis_kelamin', user.jenis_kelamin)

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            user.profile_picture = filename

        db.session.commit()
        return jsonify({
            "status" : True,
            "message": "Berhasil", 
            "data": {
                "fullname": user.fullname, 
                "email": user.email, 
                "jenis_kelamin": user.jenis_kelamin,
                "profile_picture": user.profile_picture
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_image(filename):
    directory = os.path.join(current_app.root_path, 'uploads', 'photo_profile')
    return send_from_directory(directory, filename)

def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User tidak ditemukan"}), 404
    
    return jsonify({
        "fullname": user.fullname,
        "email": user.email,
        "jenis_kelamin": user.jenis_kelamin,
        "profile_picture": user.profile_picture
    }), 200