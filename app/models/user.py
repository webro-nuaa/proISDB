# -*- coding: utf-8 -*-
"""
用户模型
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)  # 与数据库保持一致
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('root', 'admin', 'visitor'), default='visitor')
    
    # 个人信息 - 与ISElement的submitter字段对齐
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    institution = db.Column(db.String(200))
    department = db.Column(db.String(200))
    postal_address = db.Column(db.String(300))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    telephone = db.Column(db.String(50))
    
    # 系统字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系
    submitted_elements = db.relationship('ISElement', 
                                       foreign_keys='ISElement.submitter_id',
                                       backref='submitter', 
                                       lazy='dynamic')
    reviewed_elements = db.relationship('ISElement', 
                                      foreign_keys='ISElement.reviewer_id',
                                      backref='reviewer', 
                                      lazy='dynamic')
    articles = db.relationship('KnowledgeArticle', backref='author', lazy='dynamic')
    search_logs = db.relationship('SearchLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_root(self):
        """检查是否为超级管理员"""
        return self.role == 'root'
    
    def is_admin(self):
        """检查是否为管理员(不包括root)"""
        return self.role == 'admin'
    
    def has_admin_permission(self):
        """检查是否具有管理员权限(包括root和admin)"""
        return self.role in ('root', 'admin')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'institution': self.institution,
            'department': self.department,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @property
    def full_name(self):
        """获取完整姓名"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ''
