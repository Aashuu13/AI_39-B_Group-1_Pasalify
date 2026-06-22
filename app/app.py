"""
app/app.py
================================================================
Application factory.

Flask apps can be built with a plain module-level `app = Flask(...)`,
but Pasalify uses the "factory" pattern instead: create_app() builds
and returns a brand-new app instance every time it's called. This
makes the app easy to configure differently for testing vs.
production, and avoids import-order problems between blueprints.
"""

from dotenv import load_dotenv
load_dotenv()  # reads a local .env file (if present) into os.environ

from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from app.config import Config
import os

# CSRFProtect is created once at module level, then bound to whichever
# app instance create_app() builds via csrf.init_app(app).
csrf = CSRFProtect()


def create_app():
    """Build, configure, and return a fully wired Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Adds a hidden CSRF token requirement to every form (see csrf_token()
    # calls in the templates) and rejects POSTs that don't include it.
    csrf.init_app(app)

    # Make sure the folder for uploaded images exists before any upload happens
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

   
    from app.routes.auth     import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.seller   import seller_bp
    from app.routes.admin    import admin_bp
    from app.routes.store    import store_bp

    app.register_blueprint(auth_bp,     url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(seller_bp,   url_prefix='/seller')
    app.register_blueprint(admin_bp,    url_prefix='/admin')
    app.register_blueprint(store_bp,    url_prefix='/store')

    @app.route('/')
    def index():
        """Site root just forwards visitors to the customer homepage."""
        return redirect(url_for('customer.home'))

    @app.teardown_appcontext
    def close_db(e=None):
        """Runs after every request (success or error) to close the
        per-request MySQL connection opened in app/db.py."""
        from app import db
        db.close_db(e)

    return app
