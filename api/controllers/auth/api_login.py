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
                "jenis_kelamin": user.jenis_kelamin,
                "email": user.email,
                "role": user.role,
                "profile_picture": user.profile_picture
                }
            }), 200
    elif not user:
        return jsonify({"message": "Email tidak ditemukan, mohon periksa kembali email Anda"}), 404
    elif not user.check_password(data.get('password')):
        return jsonify({"message": "Password salah, mohon periksa kembali password Anda"}), 401
    else:
        return jsonify({"message": "Login gagal mohon periksa kembali email dan password Anda"}), 400
        

def api_login_by_google():
    data = request.get_json()
    id_token_from_flutter = data.get("id_token")
    access_token_from_flutter = data.get("access_token") # Ambil access_token juga

    if not id_token_from_flutter:
        return jsonify({"error": "Missing ID Token"}), 400

    try:
        # 1. Verifikasi ID Token seperti biasa
        info = id_token.verify_oauth2_token(
            id_token_from_flutter,
            requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )

        email = info.get("email")
        fullname = info.get("name")
        picture = info.get("picture")
        
        gender_google = None
        
        if access_token_from_flutter:
            try:
                people_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
                headers = {"Authorization": f"Bearer {access_token_from_flutter}"}
                response = requests.get(people_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    res_data = response.json()
                    genders = res_data.get("genders", [])
                    if genders:
                        raw_val = genders[0].get("value")
                        gender_google = "Laki Laki" if raw_val == "male" else "Perempuan"
            except Exception as e:
                print(f"Gagal mengambil gender: {e}")

        # 2. VALIDASI PENTING: Pastikan gender_google tidak None
        if not gender_google:
            gender_google = "Laki Laki"

        user = Users.query.filter_by(email=email).first()

        if not user:
            user = Users(
                email=email,
                fullname=fullname or "User Mobile",
                jenis_kelamin=gender_google,
                role="user",
                profile_picture=picture
            )
            user.set_password(secrets.token_urlsafe(16))
            db.session.add(user)
            db.session.commit()

        token_internal = create_access_token(identity=str(user.id))

        return jsonify({
            "success": True, # Tambahkan ini agar sama dengan api_login
            "message": "Login berhasil via Google",
            "access_token": token_internal,
            "users": { # Samakan strukturnya dengan login biasa
                "id": user.id,
                "fullname": user.fullname,
                "jenis_kelamin": user.jenis_kelamin,
                "email": user.email,
                "role": user.role,
                "profile_picture": user.profile_picture
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401
