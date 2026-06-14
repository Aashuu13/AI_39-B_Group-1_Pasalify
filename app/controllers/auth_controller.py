"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (Auth Controller)
==============================================================
- Inheritance: AuthController extends BaseController and gets
  _ok/_err/_q/_run/_log for free — no repetition.
- Encapsulation: Validation rules (email, password length,
  role whitelist) are hidden inside _validate_registration().
  Login logic (hash check, failed-login counter) lives inside
  login() and never leaks to the route layer.
==============================================================
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import UserModel, StoreModel
from app.utils.auth import valid_email, log_action


class AuthController(BaseController):
    """
    Handles: register, login, logout, forgot_password,
             change_password.

    Inherits from BaseController:
        _ok, _err, _warn, _info, _q, _run, _log, _notify,
        _current_user_id, _is_logged_in
    """

    # ── Private Validation (Encapsulation) ────────────────────────────────────

    def _validate_registration(self, name, email, phone, pw, pw2, role) -> list[str]:
        """
        All registration validation rules in one place.
        Returns a list of error strings (empty = valid).
        Encapsulation: controllers call this; they never repeat these checks.
        """
        errors = []
        if not name:
            errors.append('Name is required.')
        if not valid_email(email):
            errors.append('Invalid email address.')
        if len(pw) < 8:
            errors.append('Password must be at least 8 characters.')
        if pw != pw2:
            errors.append('Passwords do not match.')
        if role not in ('customer', 'seller'):
            errors.append('Invalid role selected.')
        if UserModel.find_by_email_or_phone(email, phone):
            errors.append('Email or phone already registered.')
        return errors

    # ── Public Actions ────────────────────────────────────────────────────────

    def register(self):
        """
        GET  → show registration form
        POST → validate → create user → redirect
        """
        if request.method == 'POST':
            name  = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            pw    = request.form.get('password', '')
            pw2   = request.form.get('confirm_password', '')
            role  = request.form.get('role', 'customer')

            errors = self._validate_registration(name, email, phone, pw, pw2, role)
            if errors:
                for e in errors:
                    self._err(e)
                return render_template('auth/register.html', name=name,
                                       email=email, phone=phone, role=role)

            uid = UserModel.register(name, email, phone, pw, role)
            if role == 'seller':
                session['pending_store_setup'] = uid
            self._ok('Account created! Please log in.')
            return redirect(url_for('auth.login'))

        return render_template('auth/register.html')

    def login(self):
        """
        GET  → show login form
        POST → authenticate → set session → redirect by role
        """
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            pw    = request.form.get('password', '')

            # Attempt authentication (Encapsulation: hash check inside UserModel)
            user = UserModel.find_by_email(email)

            if not user or not UserModel.authenticate(email, pw):
                if user:
                    UserModel.record_failed_login(user['id'])
                self._err('Invalid email or password.')
                return render_template('auth/login.html', email=email)

            if not user['is_active']:
                self._err('Your account has been deactivated.')
                return render_template('auth/login.html')

            # Successful login
            UserModel.update_last_login(user['id'])
            session.clear()
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            session['email']   = user['email']
            self._log('login')

            # Role-based redirect (Polymorphism: each role routes differently)
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'seller':
                store = StoreModel.find_by_user(user['id'])
                return redirect(url_for('seller.setup') if not store
                                else url_for('seller.dashboard'))
            return redirect(url_for('customer.home'))

        return render_template('auth/login.html')

    def logout(self):
        """Clear session and redirect to login."""
        self._log('logout')
        session.clear()
        self._info('Logged out successfully.')
        return redirect(url_for('auth.login'))

    def forgot_password(self):
        """
        GET  → show forgot-password form
        POST → stub (would send reset email in production)
        """
        if request.method == 'POST':
            # Encapsulation: don't reveal whether the email exists
            self._info('If that email exists, a reset link has been sent.')
            return redirect(url_for('auth.login'))
        return render_template('auth/forgot_password.html')

    def change_password(self):
        """
        GET  → show change-password form
        POST → verify old password → update → redirect
        """
        if not self._is_logged_in():
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            user   = UserModel.find_by_id(self._current_user_id())

            # Encapsulation: password verification inside UserModel.authenticate
            if not UserModel.authenticate(user['email'], old_pw):
                self._err('Current password is incorrect.')
            elif len(new_pw) < 8:
                self._err('New password must be at least 8 characters.')
            else:
                UserModel.change_password(self._current_user_id(), new_pw)
                self._log('change_password')
                self._ok('Password updated successfully.')
                return redirect(url_for('customer.profile'))

        return render_template('auth/change_password.html')


# ── Singleton instance (used by routes) ──────────────────────────────────────
auth_controller = AuthController()
