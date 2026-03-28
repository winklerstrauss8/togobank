"""TogoBank Digital — Flask Application Factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name='development'):
    """Crée et configure l'application Flask."""
    app = Flask(
        __name__,
        static_folder='../static',
        template_folder='templates'
    )
    app.config.from_object(config.get(config_name, config['default']))

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    limiter.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.routes.topup import topup_bp
    from app.routes.admin import admin_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(accounts_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
    app.register_blueprint(topup_bp, url_prefix='/api/v1/topup')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')

    # Create tables
    with app.app_context():
        from app.models import user, compte, transaction, recharge, carte, beneficiaire, notification, audit_log
        db.create_all()

    return app
