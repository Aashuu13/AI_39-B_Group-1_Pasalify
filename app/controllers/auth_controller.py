"""
==============================================================
MY FEATURES – Auth Controller
Sprint 1: US 1.3 – Reset Account INFO (Forgot/Change Password)
==============================================================
Only includes: forgot_password, change_password
Login and register are kept as minimal stubs so the app boots
and the session works for other features.
==============================================================
"""

from flask import render_template, request, redirect, url_for, session

from app.controllers.base_controller import BaseController
from app.models import UserModel, StoreModel
from app.utils.auth import valid_email, log_action


class AuthController(BaseController):

    # ── Minimal stubs to keep routing/session working ─────────────────────────

    def register(self):
        if request.method == 'POST':
            name  = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            pw    = request.form.get('password', '')
            pw2   = request.form.get('confirm_password', '')
            role  = request.form.get('role', 'customer')
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
            if errors:
                for e in errors:
                    self._err(e)
                return render_template('auth/register.html', name=name, email=email, phone=phone, role=role)
            uid = UserModel.register(name, email, phone, pw, role)
            if role == 'seller':
                session['pending_store_setup'] = uid
            self._ok('Account created! Please log in.')
            return redirect(url_for('auth.login'))
        return render_template('auth/register.html')

    def login(self):
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            pw    = request.form.get('password', '')
            user  = UserModel.find_by_email(email)
            if not user or not UserModel.authenticate(email, pw):
                if user:
                    UserModel.record_failed_login(user['id'])
                self._err('Invalid email or password.')
                return render_template('auth/login.html', email=email)
            if not user['is_active']:
                self._err('Your account has been deactivated.')
                return render_template('auth/login.html')
            UserModel.update_last_login(user['id'])
            session.clear()
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            session['email']   = user['email']
            self._log('login')
            if user['role'] == 'admin':
                return redirect(url_for('auth.login'))  # no admin in this build
            elif user['role'] == 'seller':
                store = StoreModel.find_by_user(user['id'])
                return redirect(url_for('seller.setup') if not store else url_for('seller.products'))
            return redirect(url_for('customer.home'))
        return render_template('auth/login.html')

    def logout(self):
        self._log('logout')
        session.clear()
        self._info('Logged out successfully.')
        return redirect(url_for('auth.login'))

    # ── Sprint 1: US 1.3 – Reset Account INFO ─────────────────────────────────

    def forgot_password(self):
        """
        GET  → Show forgot-password form (user enters email).
        POST → Look up the account and simulate sending a reset link.
        In a real system this would generate a token and email it.
        """
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            if not valid_email(email):
                self._err('Please enter a valid email address.')
                return render_template('auth/forgot_password.html')
            # Security: don't reveal whether the email exists
            self._info('If that email is registered, a reset link has been sent.')
            return redirect(url_for('auth.login'))
        return render_template('auth/forgot_password.html')

    def change_password(self):
        """
        GET  → Show change-password form for logged-in users.
        POST → Verify old password → update to new → redirect to profile.
        This is the 'Reset Account INFO' feature for authenticated users.
        """
        if not self._is_logged_in():
            self._warn('Please log in to change your password.')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            old_pw  = request.form.get('old_password', '')
            new_pw  = request.form.get('new_password', '')
            new_pw2 = request.form.get('confirm_new_password', '')
            user    = UserModel.find_by_id(self._current_user_id())

            if not UserModel.authenticate(user['email'], old_pw):
                self._err('Current password is incorrect.')
            elif len(new_pw) < 8:
                self._err('New password must be at least 8 characters.')
            elif new_pw != new_pw2:
                self._err('New passwords do not match.')
            else:
                UserModel.change_password(self._current_user_id(), new_pw)
                self._log('change_password')
                self._ok('Password updated successfully!')
                return redirect(url_for('customer.profile'))

        return render_template('auth/change_password.html')


# Singleton used by routes
auth_controller = AuthController()
