from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from app.utils.config import Config
import os

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    csrf.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.auth     import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.seller   import seller_bp
    from app.routes.admin    import admin_bp

    app.register_blueprint(auth_bp,     url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(seller_bp,   url_prefix='/seller')
    app.register_blueprint(admin_bp,    url_prefix='/admin')

    @app.route('/')
    def index():
        return redirect(url_for('customer.home'))

    @app.teardown_appcontext
    def close_db(e=None):
        from app.utils import db
        db.close_db(e)

    return app
