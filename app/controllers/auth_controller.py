"""
Auth Controller — business logic for registration, login, logout,
forgot-password, and change-password.
"""
import re

from flask import render_template, request, redirect, url_for, session, flash

from app import db
from app.utils.auth import hash_password, check_password, valid_email, log_action


def register():
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        pw    = request.form.get('password', '')
        pw2   = request.form.get('confirm_password', '')
        role  = request.form.get('role', 'customer')

        errors = []
        if not name:                errors.append('Name is required.')
        if not valid_email(email):  errors.append('Invalid email.')
        if len(pw) < 8:             errors.append('Password must be at least 8 characters.')
        if pw != pw2:               errors.append('Passwords do not match.')
        if role not in ('customer', 'seller'):
            role = 'customer'

        existing = db.query(
            "SELECT id FROM users WHERE email=%s OR phone=%s", (email, phone), one=True
        )
        if existing:
            errors.append('Email or phone already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html', name=name, email=email,
                                   phone=phone, role=role)

        uid = db.execute(
            "INSERT INTO users (name,email,phone,password_hash,role) VALUES (%s,%s,%s,%s,%s)",
            (name, email, phone, hash_password(pw), role)
        )
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw    = request.form.get('password', '')
        user  = db.query("SELECT * FROM users WHERE email=%s", (email,), one=True)

        if not user or not check_password(pw, user['password_hash']):
            if user:
                db.execute("UPDATE users SET failed_logins=failed_logins+1 WHERE id=%s", (user['id'],))
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', email=email)

        if not user['is_active']:
            flash('Your account has been deactivated.', 'danger')
            return render_template('auth/login.html')

        db.execute("UPDATE users SET failed_logins=0, last_login=NOW() WHERE id=%s", (user['id'],))
        session.clear()
        session['user_id'] = user['id']
        session['name']    = user['name']
        session['role']    = user['role']
        session['email']   = user['email']
        log_action(user['id'], 'login')

        session['email']   = user['email']
        log_action(user['id'], 'login')

        # Updated to point exactly to your customer blueprint's products page
        return redirect(url_for('customer.products'))
    
    return render_template('auth/login.html')


def logout():
    uid = session.get('user_id')
    if uid:
        log_action(uid, 'logout')
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        db.query("SELECT id FROM users WHERE email=%s", (email,), one=True)
        flash('If that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        old_pw = request.form.get('old_password', '')
        new_pw = request.form.get('new_password', '')
        user   = db.query("SELECT * FROM users WHERE id=%s", (session['user_id'],), one=True)

        if not check_password(old_pw, user['password_hash']):
            flash('Current password is incorrect.', 'danger')
        elif len(new_pw) < 8:
            flash('New password must be at least 8 characters.', 'danger')
        else:
            db.execute(
                "UPDATE users SET password_hash=%s WHERE id=%s",
                (hash_password(new_pw), session['user_id'])
            )
            log_action(session['user_id'], 'change_password')
            flash('Password updated successfully.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html')