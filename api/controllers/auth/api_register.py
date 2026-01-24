from flask import request, jsonify
from config import db
from models.users import Users

def api_register():
    data = request.get_json()

    fullname = data.get('fullname')
    jenis_kelamin = data.get('jenis_kelamin')
    email = data.get('email')
    password = data.get('password')

    # Validasi field kosong
    if not fullname or not jenis_kelamin or not email or not password:
        return jsonify({"message": "Data tidak lengkap, mohon lengkapi semua"}), 400
    elif Users.query.filter_by(email=email).first():
        return jsonify({"message": "Email sudah terdaftar"}), 400
    elif len(password) < 8:
        return jsonify({"message" : "password kurang dari 8 karakter" })
    else:
        new_user = Users(
            fullname = fullname,
            jenis_kelamin = jenis_kelamin,
            email = email
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Registrasi berhasil"
            }), 201
