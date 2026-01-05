from flask import Flask, Blueprint
from api.controllers.api_report import get_report
from api.controllers.api_scans import api_scan
from api.controllers.auth.api_register import api_register
from api.controllers.auth.api_login import api_login, api_login_by_google
from api.controllers.auth.api_forgot_password import api_forgot_password ,api_reset_password
from api.controllers.api_history import get_history
# app = Flask(__name__)

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

@api_auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    return api_register()

@api_auth_bp.route('/login', methods=['POST'])
def login():
    return api_login()

@api_auth_bp.route('/login/google', methods=['POST'])
def login_by_google():
    return api_login_by_google()

@api_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    return api_forgot_password()

@api_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    return api_reset_password()

api_detect_bp = Blueprint('api_detect', __name__, url_prefix='/api/detect')
@api_detect_bp.route('/scan', methods=['POST'])
def detect_pose():
    return api_scan()

api_bp = Blueprint('api', __name__, url_prefix='/api')
@api_bp.route('/history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    return get_history(user_id)

@api_bp.route('/report/<int:user_id>', methods=['GET'])
def api_status(user_id):
    return get_report(user_id)