# -*- coding: utf-8 -*-
"""
Admin管理相关表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class CreateAdminForm(FlaskForm):
    """创建管理员表单"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=50, message='Username must be 3-50 characters')
    ])
    email = StringField('Email', validators=[
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    # Optional personal info
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    institution = StringField('Institution', validators=[Length(max=200)])
    department = StringField('Department', validators=[Length(max=200)])
    country = StringField('Country', validators=[Length(max=100)])
    
    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')
    
    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if field.data and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')
