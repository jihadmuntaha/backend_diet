import functools
from flask import request, g, jsonify, current_app, redirect, session, url_for
import jwt
from datetime import datetime, timedelta
from models.users import Users
from config import db

def create_access_token(user: Users, expires_in: int = 7 * 24 * 3600):
    payload = {
        "sub": user.id,
        "is_admin": user.is_admin,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def auth_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_access_token(token)
        if not payload:
            return jsonify({"message": "Invalid or expired token"}), 401

        user = db.session.get(Users, payload["sub"])
        if not user:
            return jsonify({"message": "User not found"}), 404

        g.current_user = user
        g.jwt_payload = payload
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_access_token(token)
        if not payload or not payload.get("is_admin"):
            return jsonify({"message": "Admin access required"}), 403

        user = db.session.get(Users, payload["sub"])
        if not user:
            return jsonify({"message": "User not found"}), 404

        g.current_user = user
        g.jwt_payload = payload
        return f(*args, **kwargs)
    return wrapper

# Untuk admin dashboard (session + Google OAuth)
def admin_login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_email" not in session:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper
