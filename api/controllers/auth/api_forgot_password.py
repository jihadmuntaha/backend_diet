from flask import request, jsonify
from flask_mail import Message
from config import db
from models.users import Users
from datetime import datetime, timedelta
from config import mail
import random
import os

def api_forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        user = Users.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "Jika email terdaftar, OTP akan dikirim"}), 200

        generate_otp = str(random.randint(100000, 999999))
        
        user.reset_token = generate_otp
        user.reset_token_expiry = datetime.now() + timedelta(minutes=10)
        db.session.commit()

        msg = Message(
            subject="Reset Password Code",
            sender=os.getenv('MAIL_USERNAME'), # Pengirim
            recipients=[email]                 # Penerima
        )
        msg.body = f"Kode OTP kamu adalah: {generate_otp}. Kode ini berlaku selama 10 menit."
        mail.send(msg) 
        return jsonify({"message": "Email terkirim"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FUNGSI GANTI PASSWORD
def api_reset_password():
    try:
        data = request.get_json()
        email = data.get('email')
        otp_input = data.get('otp')
        new_pass = data.get('new_password')

        user = Users.query.filter_by(email=email).first()

        # Validasi
        if not user or user.otp_code != otp_input:
            return jsonify({"error": "OTP Salah"}), 400
        
        if user.otp_expiry < datetime.now():
            return jsonify({"error": "OTP Kadaluarsa"}), 400

        # Reset
        user.set_password(new_pass)
        user.otp_code = None # Hapus OTP
        db.session.commit()

        return jsonify({"message": "Password sukses diganti"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
