from flask import Flask, Blueprint
from api.controllers.auth.api_register import api_register
from api.controllers.auth.api_login import api_login
from api.controllers.auth.api_forgot_password import api_forgot_password ,api_reset_password
# app = Flask(__name__)

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

@api_auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    return api_register()

@api_auth_bp.route('/login', methods=['POST'])
def login():
    return api_login()

@api_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    return api_forgot_password()

@api_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    return api_reset_password()

api_bp = Blueprint('api', __name__)
