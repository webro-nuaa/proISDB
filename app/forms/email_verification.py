# -*- coding: utf-8 -*-
"""
Email verification forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.models import User

class SendVerificationCodeForm(FlaskForm):
    """Send verification code form"""
    email = StringField('Email', validators=[
        DataRequired(message='请输入邮箱地址'),
        Email(message='邮箱格式不正确')
    ])
    
    def validate_email(self, field):
        """验证邮箱是否已被其他用户使用，并清理邮箱地址"""
        # 清理邮箱地址（去除首尾空格）
        field.data = field.data.strip() if field.data else field.data
        
        from flask_login import current_user
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user and existing_user.id != current_user.id:
            raise ValidationError('该邮箱已被其他用户使用')

class VerifyEmailForm(FlaskForm):
    """Verify email form"""
    verification_code = StringField('Verification Code', validators=[
        DataRequired(message='请输入验证码'),
        Length(min=6, max=6, message='验证码为6位数字')
    ])
