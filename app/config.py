import os

BASE = os.path.dirname(__file__)


class Config:
    SECRET_KEY         = os.environ.get('SECRET_KEY', 'pasalify-np-2026-secret')
    WTF_CSRF_ENABLED   = True
    MYSQL_HOST         = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER         = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD     = os.environ.get('MYSQL_PASSWORD', 'yubrajreule2453')
    MYSQL_DB           = os.environ.get('MYSQL_DB', 'sprint2')
    MYSQL_PORT         = int(os.environ.get('MYSQL_PORT', 3306))
    UPLOAD_FOLDER      = os.path.join(BASE, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
