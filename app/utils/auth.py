
import hashlib
import os
import re
from functools import wraps

from flask import session, redirect, url_for, flash, request

from app import db

def hash_password(pw):
    """
    Turn a plain-text password into a salted PBKDF2-SHA256 hash.

    A random 32-byte salt is generated per password so that two
    users with the same password never produce the same hash.
    The salt is stored alongside the hash (separated by ':') so
    check_password() can recompute it later.
    """
    salt = os.urandom(32)
    key  = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 260000)
    return salt.hex() + ':' + key.hex()

def check_password(pw, stored):
    """
    Verify a plain-text password against a hash produced by
    hash_password(). Returns False (instead of raising) if the
    stored value is malformed, so a corrupted row never crashes
    the login page.
    """
    try:
        salt_hex, key_hex = stored.split(':')
        key = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt_hex), 260000)
        return key.hex() == key_hex
    except Exception:
        return False

def valid_email(e):
    """Quick sanity check that a string looks like an email address.
    Used during registration — not a full RFC validator."""
    return bool(re.match(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$', e, re.I))

def login_required(f):
    """
    Route decorator used throughout the real app (customer, seller,
    and store routes): redirect guests to the login page instead of
    letting them view a page that needs a session.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """
    Decorator factory for role-based access control, used on the
    admin and seller blueprints, e.g.:

        _admin  = role_required('admin')
        admin_bp.add_url_rule('/dashboard', 'dashboard', _admin(ac.dashboard))

    Guests go to login; logged-in users with the wrong role are
    sent to the customer homepage instead.
    """
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
    """
    Write one row to activity_logs — a lightweight audit trail of
    who did what (login, product_added, seller_approved, ...).
    Used by BaseController._log() so every controller gets logging
    for free.
    """
    db.execute(
        "INSERT INTO activity_logs (user_id,action,entity_type,entity_id,ip_address) VALUES (%s,%s,%s,%s,%s)",
        (user_id, action, entity_type, entity_id, request.remote_addr)
    )

def notify(user_id, title, message, ntype='system', link=None):
    """
    Create an in-app notification row for a user (order updates,
    store approvals, support replies, etc). Read by
    CustomerController.notifications() and the notification bell
    in the navbar.
    """
    db.execute(
        "INSERT INTO notifications (user_id,title,message,type,link) VALUES (%s,%s,%s,%s,%s)",
        (user_id, title, message, ntype, link)
    )
