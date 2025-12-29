from flask import request, jsonify
from flask_jwt_extended import create_access_token
from models.users import Users
from google.oauth2 import id_token
from google.auth.transport import requests

def api_login():
    data = request.get_json()
    user = Users.query.filter_by(email=data.get('email')).first()

    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "success": True,
            "message": "Selamat anda berhasil login",
            "access_token" : access_token,
            "users" : {
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
                "role": user.role,
                "photo": user.profile_picture
                }
            }), 200
    elif not user:
        return jsonify({"message": "Email tidak ditemukan, mohon periksa kembali email Anda"}), 404
    elif not user.check_password(data.get('password')):
         return jsonify({"message": "Password salah, mohon periksa kembali password Anda"}), 401
    elif not user and not user.chek_password(data.get('password')):
        return jsonify({"message" : "Harap isi email dan password anda"}), 404
    else:
        return jsonify({"message": "Login gagal mohon periksa kembali email dan password Anda"}), 400
        

def api_login_by_google():
    token = request.json.get('token')
    
    try:
        # Verifikasi token ke Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Jika valid, ambil data user
        user_email = idinfo['email']
        user_name = idinfo['name']
        user_pic = idinfo['picture']

        # --- LOGIKA DATABASE ANDA DI SINI ---
        # 1. Cek: user = User.query.filter_by(email=user_email).first()
        # 2. Jika tidak ada: buat user baru dan simpan ke DB
        # 3. simpan ke session atau generate JWT
        
        return jsonify({
            "status": "success",
            "message": f"User {user_name} berhasil tersimpan di DB",
            "user": {"email": user_email, "name": user_name}
        }), 200

    except ValueError:
        return jsonify({"status": "error", "message": "Token tidak valid"}), 400