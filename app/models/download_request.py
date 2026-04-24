# -*- coding: utf-8 -*-
"""
Download request models
"""
from datetime import datetime, timezone
from app import db


class DownloadRequest(db.Model):
    __tablename__ = 'download_requests'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), nullable=True)
    country = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    format = db.Column(db.String(10), default='csv', nullable=False)  # 导出格式: csv 或 fasta
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.Enum('pending','approved','rejected', name='download_status'), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_comment = db.Column(db.Text, nullable=True)

    items = db.relationship('DownloadRequestItem', backref='request', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DownloadRequest {self.id} by {self.email} status={self.status}>'


class DownloadRequestItem(db.Model):
    __tablename__ = 'download_request_items'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('download_requests.id', ondelete='CASCADE'))
    is_element_id = db.Column(db.Integer, db.ForeignKey('is_elements.id'))

    def __repr__(self):
        return f'<DownloadRequestItem req={self.request_id} is_element={self.is_element_id}>'
