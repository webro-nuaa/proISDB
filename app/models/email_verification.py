# -*- coding: utf-8 -*-
"""
邮箱验证模型
"""
from datetime import datetime, timezone, timedelta
from app import db
import random
import string

class EmailVerification(db.Model):
    """邮箱验证码模型"""
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.Enum('registration', 'email_change', 'password_reset'), default='email_change')
    is_verified = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)  # 验证尝试次数
    max_attempts = db.Column(db.Integer, default=5)  # 最大尝试次数
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = db.Column(db.DateTime)
    
    # 关系
    user = db.relationship('User', backref='email_verifications')
    
    def __init__(self, user_id, email, purpose='email_change', validity_minutes=15):
        """初始化验证码"""
        self.user_id = user_id
        self.email = email
        self.purpose = purpose
        self.verification_code = self.generate_code()
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=validity_minutes)
    
    @staticmethod
    def generate_code(length=6):
        """生成随机验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def is_expired(self):
        """检查验证码是否过期"""
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires
    
    def is_locked(self):
        """检查是否因尝试次数过多而被锁定"""
        return self.attempts >= self.max_attempts
    
    def verify(self, code):
        """验证验证码"""
        if self.is_verified:
            return False, '验证码已使用'
        
        if self.is_expired():
            return False, '验证码已过期'
        
        if self.is_locked():
            return False, '验证码已被锁定，尝试次数过多'
        
        self.attempts += 1
        
        if self.verification_code == code:
            self.is_verified = True
            self.verified_at = datetime.now(timezone.utc)
            return True, '验证成功'
        
        return False, f'验证码错误，剩余 {self.max_attempts - self.attempts} 次机会'
    
    def __repr__(self):
        return f'<EmailVerification {self.email} - {self.verification_code}>'
