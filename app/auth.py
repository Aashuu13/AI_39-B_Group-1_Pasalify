"""
app/auth.py
================================================================
AUTHENTICATION decorators — "Is someone logged in at all?"
================================================================
This module only answers ONE question: whether the current
visitor has an active session. It does not know or care which
*role* that user has — that job belongs to app/authcontrol.py.

Keeping these two concerns in separate files is a small example
of the Single Responsibility Principle: each module has exactly
one reason to change.

Session keys this module depends on (set by AuthController.login
in app/controllers/auth_controller.py):
    session['user_id']  -> present only when a user is logged in
    session['role']     -> 'customer' | 'seller' | 'admin'
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Route decorator: only let logged-in users through.

    Usage:
        @app.route('/profile')
        @login_required
        def profile():
            ...

    A guest (no 'user_id' in session) is redirected to the login
    page with a flash message instead of seeing the page.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def guest_only(f):
    """
    Route decorator: the opposite of login_required.

    Useful on pages like /login or /register that only make sense
    for visitors who are NOT already signed in. An already-logged-in
    user who tries to revisit them is bounced to the homepage instead.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("customer.home"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    Route decorator: only logged-in users whose role is 'admin'.

    Two separate failure cases are handled on purpose:
      1. Not logged in at all      -> send to login.
      2. Logged in, but wrong role -> send to their own homepage,
         not to /login again (they don't need to log in twice).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("customer.home"))

        return f(*args, **kwargs)

    return decorated
