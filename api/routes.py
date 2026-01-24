from flask import Flask, Blueprint
from flask_jwt_extended import jwt_required
from api.controllers.api_recommendation import get_latest_recommendation
from api.controllers.api_report import get_report
from api.controllers.api_scans import api_scan
from api.controllers.auth.api_register import api_register
from api.controllers.auth.api_login import api_login, api_login_by_google
from api.controllers.auth.api_forgot_password import api_forgot_password ,api_reset_password
from api.controllers.api_history import get_history
from api.controllers.api_update_profile import get_image, get_user_profile, update_profile
from api.controllers.chatbot import chat
from api.controllers.feedback import feedback
from api.controllers.auth.api_change_password import handle_change_password
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

@api_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    return handle_change_password()

@api_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    return api_reset_password()

api_detect_bp = Blueprint('api_detect', __name__, url_prefix='/api/detect')
@api_detect_bp.route('/scan', methods=['POST'])
def detect_pose():
    return api_scan()

api_bp = Blueprint('api', __name__, url_prefix='/api')
@api_bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_history():
    return get_history()

@api_bp.route('/report', methods=['GET'])
@jwt_required()
def api_status():
    return get_report()

@api_bp.route('/update_profile', methods=['GET', 'POST'])
@jwt_required()
def api_update_profile():
    return update_profile()

@api_bp.route('/get_image/<filename>', methods=['GET'])
def api_get_image(filename):
    return get_image(filename)

@api_bp.route('/get_profile', methods=['GET'])
@jwt_required()
def api_get_user_profile():
    return get_user_profile()

@api_bp.route('/feedback', methods=['POST'])
@jwt_required()
def api_post_feedback():
    return feedback()

@api_bp.route('/latest_recommendation', methods=['GET'])
@jwt_required()
def api_get_latest_recommendation():
    return get_latest_recommendation()

@api_bp.route('/chatbot', methods=['GET', 'POST'])
def api_chatbot():
    return chat()   