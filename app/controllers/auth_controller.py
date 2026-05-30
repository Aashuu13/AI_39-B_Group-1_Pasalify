"""
=============================================================
OOP Concepts: INHERITANCE  &  ENCAPSULATION  (AuthController)
=============================================================
Inheritance  — AuthController extends BaseController and
               inherits _ok, _err, _q, _run, _is_logged_in,
               _current_user_id — no copy-paste needed.
Encapsulation— All validation rules live in the private
               method _validate_registration().
               Password checking is hidden inside UserModel.
               The route layer never touches raw db or flash.
=============================================================
"""

from flask import render_template, request, redirect, url_for, session

from app.controllers.base_controller import BaseController
from app.models   import UserModel
from app.utils.auth import valid_email, log_action


class AuthController(BaseController):

    def _validate_registration(self, name, email, phone, pw, pw2, role) -> list:
        errors = []
        if not name:                               errors.append('Name is required.')
        if not valid_email(email):                 errors.append('Invalid email address.')
        if len(pw) < 8:                            errors.append('Password must be at least 8 characters.')
        if pw != pw2:                              errors.append('Passwords do not match.')
        if role not in ('customer', 'seller'):     errors.append('Invalid role selected.')
        if UserModel.find_by_email_or_phone(email, phone):
            errors.append('Email or phone already registered.')
        return errors

    def register(self):
        if request.method == 'POST':
            name  = request.form.get('name',             '').strip()
            email = request.form.get('email',            '').strip().lower()
            phone = request.form.get('phone',            '').strip()
            pw    = request.form.get('password',         '')
            pw2   = request.form.get('confirm_password', '')
            role  = request.form.get('role',             'customer')

            errors = self._validate_registration(name, email, phone, pw, pw2, role)
            if errors:
                for e in errors:
                    self._err(e)
                return render_template('auth/register.html',
                                       name=name, email=email, phone=phone, role=role)

            UserModel.register(name, email, phone, pw, role)
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
            log_action(user['id'], 'login')
            return redirect(url_for('customer.products'))

        return render_template('auth/login.html')

    def logout(self):
        uid = self._current_user_id()
        if uid:
            log_action(uid, 'logout')
        session.clear()
        self._info('Logged out successfully.')
        return redirect(url_for('auth.login'))

    def forgot_password(self):
        if request.method == 'POST':
            self._info('If that email exists, a reset link has been sent.')
            return redirect(url_for('auth.login'))
        return render_template('auth/forgot_password.html')

    def change_password(self):
        if not self._is_logged_in():
            return redirect(url_for('auth.login'))
        if request.method == 'POST':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            user   = UserModel.find_by_id(self._current_user_id())
            if not UserModel.authenticate(user['email'], old_pw):
                self._err('Current password is incorrect.')
            elif len(new_pw) < 8:
                self._err('New password must be at least 8 characters.')
            else:
                UserModel.change_password(self._current_user_id(), new_pw)
                log_action(self._current_user_id(), 'change_password')
                self._ok('Password updated successfully.')
                return redirect(url_for('auth.login'))
        return render_template('auth/change_password.html')


auth_controller = AuthController()
