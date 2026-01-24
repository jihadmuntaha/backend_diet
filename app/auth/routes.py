from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session, render_template, flash
from config import db
from models.users import Users
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from urllib.parse import urlencode
import secrets

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def admin_login_local():
    if request.method == "GET":
        return render_template("admin/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = Users.query.filter_by(email=email, role="admin").first()

    if not user or not user.check_password(password):
        return render_template(
            "admin/login.html",
            error="Email atau password salah"
        )

    # SIMPAN DATA KE SESSION
    session["admin_id"] = user.id
    session["admin_email"] = user.email
    session["admin_name"] = user.fullname

    return redirect("/admin/dashboard") # Perbaikan URL


@auth_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "GET":
        return render_template("admin/register.html")

    # Ambil data dari form (Pastikan 'name' di HTML sama dengan di sini)
    fullname = request.form.get("fullname")
    jenis_kelamin = request.form.get("jenis_kelamin")
    email = request.form.get("email")
    password = request.form.get("password")
    secret = request.form.get("secret")

    ADMIN_SECRET = os.getenv("ADMIN_REGISTER_SECRET")

    # Validasi Secret Key
    if secret != ADMIN_SECRET:
        return render_template("admin/register.html", error="Secret admin salah")

    # Cek duplikasi email
    if Users.query.filter_by(email=email).first():
        return render_template("admin/register.html", error="Email sudah terdaftar")

    try:
        user = Users(
            fullname=fullname,
            jenis_kelamin=jenis_kelamin, # Perbaikan: Gunakan input user
            email=email,
            role="admin"
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        
        return redirect("/") # Redirect ke login admin
        
    except Exception as e:
        db.session.rollback()
        return render_template("admin/register.html", error=f"Database error: {str(e)}")


@auth_bp.route("/auth/google/login")
def google_login():
    google_client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["OAUTH_REDIRECT_URI"]

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

@auth_bp.route("/auth/google/callback")
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
    access_token = token_resp.get("access_token")

    try:
        info = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )
    except Exception as e:
        return f"Invalid ID token: {str(e)}", 400

    # Ambil Gender (Opsional)
    final_gender = "L"
    try:
        people_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
        headers = {"Authorization": f"Bearer {access_token}"}
        people_resp = requests.get(people_url, headers=headers).json()
        genders = people_resp.get("genders", [])
        if genders:
            val = genders[0].get("value")
            final_gender = "P" if val == "female" else "L"
    except:
        pass

    email = info.get("email")
    fullname = info.get("name")

    user = Users.query.filter_by(email=email).first()
    if not user:
        user = Users(
            email=email, 
            fullname=fullname or "Google User",
            jenis_kelamin=final_gender,
            role="admin"
        )
        user.set_password(secrets.token_urlsafe(16))
        db.session.add(user)
        db.session.commit()

    session["admin_id"] = user.id
    session["admin_email"] = user.email
    session["admin_name"] = user.fullname

    # Redirect absolut ke domain Ngrok
    return redirect("/admin/dashboard")

# Logout admin
@auth_bp.route("/auth/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/")