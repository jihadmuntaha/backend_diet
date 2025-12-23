from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session, render_template
from app import db
from app.models.user import User
from .utils import create_access_token
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from urllib.parse import urlencode
import secrets

auth_bp = Blueprint("auth", __name__, url_prefix="/")

# ========== JSON API: Register & Login (MOBILE) ======

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(user)
    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(user)
    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 200


# ========== ADMIN LOGIN MANUAL (WEB) =================

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login_local():
    if request.method == "GET":
        return render_template("admin/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email, is_admin=True).first()

    if not user or not user.check_password(password):
        return render_template(
            "admin/login.html",
            error="Email atau password salah"
        )

    # ✔ SIMPAN DATA ADMIN KE SESSION
    session["admin_id"] = user.id
    session["admin_email"] = user.email
    session["admin_name"] = user.name 

    return redirect(url_for("admin.dashboard"))


# ========== ADMIN REGISTER (WITH SECRET) =============

@auth_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "GET":
        return render_template("admin/register.html")

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    secret = request.form.get("secret")

    ADMIN_SECRET = os.getenv("ADMIN_REGISTER_SECRET", "REGISTER_ADMIN_2025")

    if secret != ADMIN_SECRET:
        return render_template(
            "admin/register.html",
            error="Secret admin salah"
        )

    if User.query.filter_by(email=email).first():
        return render_template(
            "admin/register.html",
            error="Email sudah terdaftar"
        )

    user = User(
        name=name,
        email=email,
        is_admin=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.admin_login_local"))


# =====================================================
# ========== GOOGLE OAUTH (ADMIN) =====================
# =====================================================


@auth_bp.route("/auth/google/login", endpoint="google_login")
def google_login():
    google_client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["OAUTH_REDIRECT_URI"]

    # state untuk keamanan & konsistensi
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": google_client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    auth_url = f"{auth_endpoint}?{urlencode(params)}"

    return redirect(auth_url)

@auth_bp.route("/auth/google/callback", methods=["GET"])
def google_callback():
    code = request.args.get("code")
    if not code:
        return "Missing authorization code", 400

    token_endpoint = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": current_app.config["OAUTH_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }

    token_resp = requests.post(token_endpoint, data=data).json()

    if "id_token" not in token_resp:
        return f"Failed to obtain ID token: {token_resp}", 400

    id_token_jwt = token_resp["id_token"]

    try:
        info = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )
    except Exception as e:
        return f"Invalid ID token: {str(e)}", 400

    email = info.get("email")
    name = info.get("name")

    if not email:
        return "Google did not return an email", 400

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()


    session["admin_id"] = user.id
    session["admin_email"] = user.email
    session["admin_name"] = user.name

    return redirect(url_for("admin.dashboard"))


# =====================================================
# ========== ADMIN LOGOUT =============================
# =====================================================

@auth_bp.route("/auth/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("auth.admin_login_local"))
