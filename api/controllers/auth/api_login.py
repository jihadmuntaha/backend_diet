import secrets
from flask import current_app, request, jsonify
from flask_jwt_extended import create_access_token
from config import db
from models.users import Users
from google.oauth2 import id_token
from google.auth.transport import requests

def api_login():
    data = request.get_json()

    user = Users.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({
            "success": False,
            "message": "Email dan password wajib diisi"
        }), 400
    
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
    else:
        return jsonify({"message": "Login gagal mohon periksa kembali email dan password Anda"}), 400
        

def api_login_by_google():
    data = request.json
    id_token_from_flutter = data.get("id_token")

    if not id_token_from_flutter:
        return jsonify({"error": "Missing ID Token"}), 400

    try:
        info = id_token.verify_oauth2_token(
            id_token_from_flutter,
            requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )

        email = info.get("email")
        fullname = info.get("name")
        picture = info.get("picture")

        # 2. Cari user di database
        user = Users.query.filter_by(email=email).first()

        if not user:
            user = Users(
                email=email,
                fullname=fullname or "User Mobile",
                jenis_kelamin="L",
                role="user",
                profile_picture=picture
            )
            # Password random karena kolom password_hash NOT NULL
            user.set_password(secrets.token_urlsafe(16))
            db.session.add(user)
            db.session.commit()

        # 3. Buat Token JWT internal (Gunakan fungsi create_access_token Anda)
        # Token ini yang akan digunakan Flutter untuk akses API lain
        token_internal = create_access_token(identity=str(user.id))

        return jsonify({
            "success": True, # Tambahkan ini agar sama dengan api_login
            "message": "Login berhasil via Google",
            "access_token": token_internal,
            "users": { # Samakan strukturnya dengan login biasa
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
                "role": user.role,
                "photo": user.profile_picture
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401