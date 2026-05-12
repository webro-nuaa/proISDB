# -*- coding: utf-8 -*-
import os
import sys
from datetime import timedelta
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))


def _require_env(key):
    value = os.environ.get(key)
    if not value:
        print(f"[FATAL] Environment variable {key} is required but not set. "
              f"Please set it in your .env file.", file=sys.stderr)
        sys.exit(1)
    return value


class Config:
    VERSION = '2.0.0'
    SECRET_KEY = _require_env('SECRET_KEY')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = _require_env('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'insertq_db')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{quote_plus(MYSQL_USER)}:{quote_plus(MYSQL_PASSWORD)}'
        f'@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 5,
        'max_overflow': 10
    }

    UPLOAD_FOLDER = os.path.join(basedir, '..', 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', '16')) * 1024 * 1024
    allowed_ext_str = os.environ.get('ALLOWED_EXTENSIONS', 'xlsx,xls,csv,txt,jpg,jpeg,png,gif')
    ALLOWED_EXTENSIONS = set(ext.strip() for ext in allowed_ext_str.split(','))

    RECORDS_PER_PAGE = int(os.environ.get('RECORDS_PER_PAGE', '20'))
    SEARCH_RESULTS_PER_PAGE = int(os.environ.get('SEARCH_RESULTS_PER_PAGE', '12'))

    session_days = int(os.environ.get('SESSION_LIFETIME_DAYS', '7'))
    PERMANENT_SESSION_LIFETIME = timedelta(days=session_days)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ['true', 'on', '1']
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    MAIL_DEBUG = False

    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'redis')
    SESSION_REDIS = os.environ.get('SESSION_REDIS_URL', 'redis://localhost:6379/2')

    RESTX_MASK_SWAGGER = False
    RESTX_VALIDATE = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    CACHE_TYPE = 'SimpleCache'
    SESSION_TYPE = 'filesystem'
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    LOG_LEVEL = 'INFO'
    TEMPLATES_AUTO_RELOAD = os.environ.get('TEMPLATES_AUTO_RELOAD', 'false').lower() in ['true', 'on', '1']

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')

            file_handler = RotatingFileHandler(
                'logs/insertq.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('proISDB startup')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
