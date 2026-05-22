from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from app.config import Config
import os

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    csrf.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints — Sprint 1 only
    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.teardown_appcontext
    def close_db(e=None):
        from app import db
        db.close_db(e)

    return app
