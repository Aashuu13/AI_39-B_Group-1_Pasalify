import hashlib
import os
import re
from functools import wraps

from flask import session, redirect, url_for, flash, request

from app import db

def hash_password(pw):
    salt = os.urandom(32)
    key  = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 260000)
    return salt.hex() + ':' + key.hex()

def check_password(pw, stored):
    try:
        salt_hex, key_hex = stored.split(':')
        key = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt_hex), 260000)
        return key.hex() == key_hex
    except Exception:
        return False

def valid_email(e):
    return bool(re.match(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$', e, re.I))

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('customer.home'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def log_action(user_id, action, entity_type=None, entity_id=None):
    db.execute(
        "INSERT INTO activity_logs (user_id,action,entity_type,entity_id,ip_address) VALUES (%s,%s,%s,%s,%s)",
        (user_id, action, entity_type, entity_id, request.remote_addr)
    )

def notify(user_id, title, message, ntype='system', link=None):
    db.execute(
        "INSERT INTO notifications (user_id,title,message,type,link) VALUES (%s,%s,%s,%s,%s)",
        (user_id, title, message, ntype, link)
    )
