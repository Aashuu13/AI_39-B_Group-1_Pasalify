
import os

BASE = os.path.dirname(__file__)

class Config:
    """Flask reads every UPPERCASE attribute on this class as a
    config key via app.config.from_object(Config)."""

    SECRET_KEY         = os.environ.get('SECRET_KEY', 'pasalify-np-2026-secret')

    WTF_CSRF_ENABLED   = True

    MYSQL_HOST         = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER         = os.environ.get('MYSQL_USER', 'root')
<<<<<<< HEAD
    MYSQL_PASSWORD     = os.environ.get('MYSQL_PASSWORD', 'aashuNEXTdoor2007_')
    MYSQL_DB           = os.environ.get('MYSQL_DB', 'pasalify3_db')
=======
    MYSQL_PASSWORD     = os.environ.get('MYSQL_PASSWORD', '@ayushma1234')
    MYSQL_DB           = os.environ.get('MYSQL_DB', 'sprint5')
>>>>>>> origin/aayushma
    MYSQL_PORT         = int(os.environ.get('MYSQL_PORT', 3306))

    UPLOAD_FOLDER      = os.path.join(BASE, 'static', 'uploads')
<<<<<<< HEAD

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
=======
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
>>>>>>> origin/sandesh
