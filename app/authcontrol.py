<<<<<<< HEAD
=======
"""
app/authcontrol.py
================================================================
AUTHORIZATION decorators — "Is this logged-in user ALLOWED here?"
================================================================
Where app/auth.py only checks "is anyone logged in?", this module
checks "does the logged-in user have the right ROLE for this
page?" by comparing session['role'] against one or more roles
that are allowed to pass.

This is Role-Based Access Control (RBAC): instead of writing a
new permission check for every page, every view is protected by
declaring which role(s) it is for, e.g. role_required('admin').

A login_required copy is included here too (instead of importing
it from app/auth.py) so this module can be used completely on its
own if a future page only needs role-checking without pulling in
the whole auth module.
"""
>>>>>>> origin/aayushma

from functools import wraps
from flask import session, redirect, url_for, flash

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def login_required(f):
    """
    Route decorator: only let logged-in users through.
    See app/auth.py for the authentication-only version of this
    same idea — this copy exists so authcontrol.py has no
    dependency on auth.py.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def role_required(*roles):
    """
    Decorator FACTORY for role-based access control.

    Call it with one or more allowed role names and it returns a
    real decorator:

        @role_required('admin')
        def dashboard(): ...

        @role_required('admin', 'seller')
        def shared_page(): ...

    Guests are sent to login; logged-in users with the wrong role
    are sent home with a flash message instead of a confusing
    permission error.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("auth.login"))

            if session.get("role") not in roles:
                flash("You do not have permission to view that page.", "danger")
                return redirect(url_for("customer.home"))

            return f(*args, **kwargs)
        return decorated
    return decorator

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def admin_required(f):
    """Shortcut so '@admin_required' can be used directly,
    without having to write '@role_required('admin')'."""
    return role_required("admin")(f)

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def seller_required(f):
    """Shortcut so '@seller_required' can be used directly,
    without having to write '@role_required('seller')'."""
    return role_required("seller")(f)

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def customer_required(f):
    """Shortcut so '@customer_required' can be used directly,
    without having to write '@role_required('customer')'."""
    return role_required("customer")(f)
