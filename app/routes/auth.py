"""
Auth routes — Sprint 1: US 1.3 Reset Account INFO
Includes login/register/logout as minimal session support,
plus forgot_password and change_password (the sprint feature).
"""
from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

auth_bp.add_url_rule('/register',        'register',        auth_controller.register,        methods=['GET', 'POST'])
auth_bp.add_url_rule('/login',           'login',           auth_controller.login,           methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout',          'logout',          auth_controller.logout)

# Sprint 1 – US 1.3: Reset Account INFO
auth_bp.add_url_rule('/forgot-password', 'forgot_password', auth_controller.forgot_password, methods=['GET', 'POST'])
auth_bp.add_url_rule('/change-password', 'change_password', auth_controller.change_password, methods=['GET', 'POST'])
