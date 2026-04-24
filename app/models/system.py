# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from app import db


class SubmissionHistory(db.Model):
    __tablename__ = 'submission_history'

    id = db.Column(db.Integer, primary_key=True)
    is_element_id = db.Column(db.Integer, db.ForeignKey('is_elements.id', ondelete='CASCADE'), nullable=False)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.Enum('create', 'update', 'delete'), nullable=False)
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    submission_reason = db.Column(db.Text)
    review_comment = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime)

    submitter = db.relationship('User', foreign_keys=[submitter_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

    def __repr__(self):
        return f'<SubmissionHistory {self.id}>'


class BatchImport(db.Model):
    __tablename__ = 'batch_imports'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    total_records = db.Column(db.Integer, nullable=False)
    successful_records = db.Column(db.Integer, default=0)
    failed_records = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('processing', 'completed', 'failed'), default='processing')
    error_log = db.Column(db.Text)
    imported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)

    importer = db.relationship('User', backref='batch_imports')

    def __repr__(self):
        return f'<BatchImport {self.filename}>'


class SearchLog(db.Model):
    __tablename__ = 'search_logs'

    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(500), nullable=False)
    search_type = db.Column(db.String(50), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<SearchLog {self.search_term}>'

    @classmethod
    def log_search(cls, search_term, search_type, results_count, user=None, request=None):
        log = cls(
            search_term=search_term,
            search_type=search_type,
            results_count=results_count,
            user_id=user.id if user and user.is_authenticated else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(log)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return log


class PageView(db.Model):
    __tablename__ = 'page_views'

    id = db.Column(db.Integer, primary_key=True)
    page_type = db.Column(db.Enum('is_element', 'knowledge_article', 'home', 'search', 'auth', 'other'),
                         nullable=False)
    page_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referer = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<PageView {self.page_type}:{self.page_id}>'

    _pending_views = []

    @classmethod
    def log_view(cls, page_type, page_id=None, user=None, request=None):
        view = cls(
            page_type=page_type,
            page_id=page_id,
            user_id=user.id if user and user.is_authenticated else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            referer=request.referrer if request else None
        )
        cls._pending_views.append(view)
        if len(cls._pending_views) >= 10:
            cls._flush_pending()
        return view

    @classmethod
    def _flush_pending(cls):
        if not cls._pending_views:
            return
        try:
            for view in cls._pending_views:
                db.session.add(view)
            db.session.commit()
        except Exception:
            db.session.rollback()
        finally:
            cls._pending_views.clear()

    @classmethod
    def flush(cls):
        cls._flush_pending()


class SystemConfig(db.Model):
    __tablename__ = 'system_configs'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text)
    description = db.Column(db.Text)
    config_type = db.Column(db.Enum('string', 'number', 'boolean', 'json'), default='string')
    is_editable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'

    @classmethod
    def get_value(cls, key, default=None):
        config = cls.query.filter_by(config_key=key).first()
        if not config:
            return default

        value = config.config_value
        if config.config_type == 'boolean':
            return value.lower() in ['true', '1', 'yes', 'on']
        elif config.config_type == 'number':
            try:
                return int(value) if '.' not in value else float(value)
            except ValueError:
                return default
        elif config.config_type == 'json':
            try:
                import json
                return json.loads(value)
            except (ValueError, TypeError):
                return default

        return value

    @classmethod
    def set_value(cls, key, value, description=None):
        config = cls.query.filter_by(config_key=key).first()
        if config:
            config.config_value = str(value)
            config.updated_at = datetime.now(timezone.utc)
        else:
            config = cls(
                config_key=key,
                config_value=str(value),
                description=description
            )
            db.session.add(config)

        db.session.commit()
        return config


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='admin_logs')

    def __repr__(self):
        return f'<AdminLog {self.action}>'

    @classmethod
    def log_action(cls, user, action, resource_type, resource_id=None, details=None, request=None):
        log = cls(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(log)
        db.session.commit()
        return log
