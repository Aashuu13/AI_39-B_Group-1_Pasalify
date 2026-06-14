"""
==============================================================
OOP: Routes wire URLs → Controller instance methods.
Each controller is a class instance (AuthController).
Bound methods are passed directly as Flask view functions.
==============================================================
"""
from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

auth_bp.add_url_rule('/register',        'register',        auth_controller.register,        methods=['GET', 'POST'])
auth_bp.add_url_rule('/login',           'login',           auth_controller.login,           methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout',          'logout',          auth_controller.logout)
auth_bp.add_url_rule('/forgot-password', 'forgot_password', auth_controller.forgot_password, methods=['GET', 'POST'])
auth_bp.add_url_rule('/change-password', 'change_password', auth_controller.change_password, methods=['GET', 'POST'])