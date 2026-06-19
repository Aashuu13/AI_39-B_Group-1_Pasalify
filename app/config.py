"""
app/config.py
================================================================
Central configuration for the Flask app.

All values are read from environment variables first (so a real
deployment can override them with a .env file or server-level
env vars), falling back to local-development defaults so the
project still runs out of the box on a fresh clone.
"""

import os

# Absolute path to the 'app' folder, used to build other paths below
BASE = os.path.dirname(__file__)


class Config:
    """Flask reads every UPPERCASE attribute on this class as a
    config key via app.config.from_object(Config)."""

    # Used by Flask to sign session cookies and CSRF tokens
    SECRET_KEY         = os.environ.get('SECRET_KEY', 'pasalify-np-2026-secret')

    # Flask-WTF: enables CSRF protection on all forms
    WTF_CSRF_ENABLED   = True

    # MySQL connection settings (see app/db.py)
    MYSQL_HOST         = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER         = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD     = os.environ.get('MYSQL_PASSWORD', 'admin@123')
    MYSQL_DB           = os.environ.get('MYSQL_DB', 'sprint2')
    MYSQL_PORT         = int(os.environ.get('MYSQL_PORT', 3306))

    # Where uploaded product/store images are saved on disk
    UPLOAD_FOLDER      = os.path.join(BASE, 'static', 'uploads')

    # Reject uploads larger than 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
