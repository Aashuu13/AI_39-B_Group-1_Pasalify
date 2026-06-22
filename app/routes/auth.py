"""
app/routes/auth.py
================================================================
OOP concept on display: routes are just URL → method WIRING.

Each line below maps one URL path + HTTP method to a bound
method on the auth_controller singleton (an instance of
AuthController). Flask calls that exact method when a matching
request comes in — there's no logic here at all, just plumbing.
"""

from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

# GET shows the form, POST submits it — same URL, same controller method
auth_bp.add_url_rule('/register',        'register',        auth_controller.register,        methods=['GET', 'POST'])
auth_bp.add_url_rule('/login',           'login',           auth_controller.login,           methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout',          'logout',          auth_controller.logout)
auth_bp.add_url_rule('/forgot-password', 'forgot_password', auth_controller.forgot_password, methods=['GET', 'POST'])
auth_bp.add_url_rule('/change-password', 'change_password', auth_controller.change_password, methods=['GET', 'POST'])
