# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_caching import Cache
from dotenv import load_dotenv

load_dotenv()

from config.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()
cache = Cache()

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri=redis_url
)


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_dsn and not app.config.get('TESTING'):
        import sentry_sdk
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_sdk.integrations.flask.FlaskIntegration()],
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            environment=config_name,
        )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    if app.config.get('TESTING'):
        app.config['RATELIMIT_ENABLED'] = False
    limiter.init_app(app)
    cache.init_app(app)

    if app.config.get('TESTING'):
        app.config['SESSION_TYPE'] = 'filesystem'
    else:
        try:
            import redis as redis_module
            session_redis_url = app.config.get('SESSION_REDIS', 'redis://localhost:6379/2')
            app.config['SESSION_TYPE'] = 'redis'
            app.config['SESSION_REDIS'] = redis_module.from_url(session_redis_url)
        except ImportError:
            pass
    from flask_session import Session
    Session(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.views.search import search as search_blueprint
    app.register_blueprint(search_blueprint, url_prefix='/search')

    from app.views.knowledge import knowledge as knowledge_blueprint
    app.register_blueprint(knowledge_blueprint, url_prefix='/knowledge')

    from app.views.submission import submission as submission_blueprint
    app.register_blueprint(submission_blueprint, url_prefix='/submission')

    from app.views.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.views.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from app.views.blast import bp as blast_blueprint
    app.register_blueprint(blast_blueprint)

    register_error_handlers(app)
    register_template_helpers(app)

    return app


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        from flask import render_template
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500


def register_template_helpers(app):
    from datetime import datetime
    from flask import url_for
    from app.utils.template_filters import register_filters

    register_filters(app)

    @app.template_global()
    def modify_query(**new_values):
        from flask import request
        args = request.args.copy()
        for key, value in new_values.items():
            args[key] = value
        return '{}?{}'.format(request.path, args.to_query_string())

    @app.context_processor
    def utility_processor():
        def get_pending_submissions_count():
            try:
                from app.models import ISElement
                return ISElement.query.filter_by(status='pending').count()
            except Exception:
                return 0

        def get_markdown_css():
            try:
                from app.utils.markdown_helper import MarkdownProcessor
                return MarkdownProcessor.get_css()
            except Exception:
                return ''

        return {
            'current_year': datetime.now().year,
            'app_name': 'proISDB',
            'get_pending_submissions_count': get_pending_submissions_count,
            'get_markdown_css': get_markdown_css
        }
