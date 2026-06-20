"""
app/controllers/auth_controller.py
================================================================
OOP concepts on display: INHERITANCE + ENCAPSULATION

    - Inheritance:   AuthController extends BaseController, so
      self._ok / self._err / self._q / self._run / self._log all
      work here without being redefined.
    - Encapsulation: every validation rule (email format,
      password length, duplicate-account check, role whitelist)
      lives inside the private _validate_registration() helper.
      The login() method's password-hash comparison is likewise
      hidden inside UserModel.authenticate() — this class never
      touches a raw password hash.

Handles: register, login, logout, forgot_password, change_password.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import UserModel, StoreModel
from app.utils.auth import valid_email, log_action


class AuthController(BaseController):
    """
    Handles every authentication-related page: register, login,
    logout, forgot_password, change_password.

    Inherited from BaseController:
        _ok, _err, _warn, _info, _q, _run, _log, _notify,
        _current_user_id, _is_logged_in
    """

    # ── Private validation (Encapsulation) ──────────────────────────────────

    def _validate_registration(self, name, email, phone, pw, pw2, role) -> list[str]:
        """
        Run every registration rule in one place and return a list
        of error messages (empty list = the form is valid). Keeping
        this separate from register() makes it easy to unit-test the
        rules on their own, and keeps register() focused on the
        GET/POST flow rather than validation details.
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

    # ── Public actions (bound directly to routes) ───────────────────────────

    def register(self):
        """
        GET  -> show the empty registration form.
        POST -> validate the submitted data; on success create the
                user and send them to login; on failure re-render the
                form with the typed values preserved and error flashes.
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
                # Remembered so the seller can be nudged into the
                # store-setup wizard right after their first login.
                session['pending_store_setup'] = uid
            self._ok('Account created! Please log in.')
            return redirect(url_for('auth.login'))

        return render_template('auth/register.html')

    def login(self):
        """
        GET  -> show the login form.
        POST -> verify credentials, start a session, and redirect
                the user to the homepage that matches their role.
        """
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            pw    = request.form.get('password', '')

            # Encapsulation: the hash comparison happens inside
            # UserModel.authenticate(); this method never sees a raw hash.
            user = UserModel.find_by_email(email)

            if not user or not UserModel.authenticate(email, pw):
                if user:
                    UserModel.record_failed_login(user['id'])
                self._err('Invalid email or password.')
                return render_template('auth/login.html', email=email)

            if not user['is_active']:
                self._err('Your account has been deactivated.')
                return render_template('auth/login.html')

            # Successful login: reset any old session data, then store
            # just enough info in the session to avoid a DB lookup on
            # every single request.
            UserModel.update_last_login(user['id'])
            session.clear()
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            session['email']   = user['email']
            self._log('login')

            # Polymorphism in spirit: the same login() method produces a
            # different redirect depending on the user's role.
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'seller':
                store = StoreModel.find_by_user(user['id'])
                return redirect(url_for('seller.setup') if not store
                                else url_for('seller.dashboard'))
            return redirect(url_for('customer.home'))

        return render_template('auth/login.html')

    def logout(self):
        """Clear the whole session and send the user back to login."""
        self._log('logout')
        session.clear()
        self._info('Logged out successfully.')
        return redirect(url_for('auth.login'))

    def forgot_password(self):
        """
        GET  -> show the forgot-password form.
        POST -> placeholder flow (a real deployment would email a
                reset link here). On purpose, the message is the same
                whether or not the email exists, so this endpoint
                can't be used to discover which emails are registered.
        """
        if request.method == 'POST':
            self._info('If that email exists, a reset link has been sent.')
            return redirect(url_for('auth.login'))
        return render_template('auth/forgot_password.html')

    def change_password(self):
        """
        GET  -> show the change-password form (must already be logged in).
        POST -> verify the current password, then save the new one.
        """
        if not self._is_logged_in():
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            user   = UserModel.find_by_id(self._current_user_id())

            # Re-using authenticate() here means the password-check
            # logic only ever lives in one place in the whole app.
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


# ── Singleton instance imported by app/controllers/__init__.py and routes ──
auth_controller = AuthController()
