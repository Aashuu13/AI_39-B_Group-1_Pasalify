from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register',        methods=['GET', 'POST'])(auth_controller.register)
auth_bp.route('/login',           methods=['GET', 'POST'])(auth_controller.login)
auth_bp.route('/logout')(auth_controller.logout)
auth_bp.route('/forgot-password', methods=['GET', 'POST'])(auth_controller.forgot_password)
auth_bp.route('/change-password', methods=['GET', 'POST'])(auth_controller.change_password)
