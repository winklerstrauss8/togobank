import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///togobank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@togobank.tg')

    # Mobile Money APIs
    MIXX_API_URL = os.getenv('MIXX_API_URL', 'https://api.mixx.tg/v1')
    MIXX_API_KEY = os.getenv('MIXX_API_KEY', '')
    MIXX_SECRET = os.getenv('MIXX_SECRET', '')
    FLOOZ_API_URL = os.getenv('FLOOZ_API_URL', 'https://api.flooz.tg/v1')
    FLOOZ_API_KEY = os.getenv('FLOOZ_API_KEY', '')
    FLOOZ_SECRET = os.getenv('FLOOZ_SECRET', '')

    # Rate Limiting
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_STORAGE_URL = 'memory://'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
