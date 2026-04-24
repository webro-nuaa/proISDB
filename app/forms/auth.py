# -*- coding: utf-8 -*-
"""
认证相关表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[
        DataRequired(message='Please enter username'),
        Length(1, 50, message='Username must be 1-50 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter password')
    ])
    remember_me = BooleanField('Remember me')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    old_password = PasswordField('Current Password', validators=[
        DataRequired(message='Please enter current password')
    ])
    password = PasswordField('New Password', validators=[
        DataRequired(message='Please enter new password'),
        Length(6, 128, message='Password must be 6-128 characters')
    ])
    password_confirm = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm new password'),
        EqualTo('password', message='Passwords do not match')
    ])

class ProfileForm(FlaskForm):
    """Profile form"""
    first_name = StringField('First Name', validators=[
        DataRequired(message='Please enter first name'),
        Length(1, 50, message='First name must be 1-50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Please enter last name'),
        Length(1, 50, message='Last name must be 1-50 characters')
    ])
    
    institution = StringField('Institution', validators=[
        DataRequired(message='Please enter institution'),
        Length(1, 200, message='Institution must be 1-200 characters')
    ])
    
    department = StringField('Department', validators=[
        Optional(),
        Length(0, 200, message='Department must be at most 200 characters')
    ])
    
    country = StringField('Country', validators=[
        DataRequired(message='Please enter country'),
        Length(1, 100, message='Country must be 1-100 characters')
    ])
    
    telephone = StringField('Telephone', validators=[
        Optional(),
        Length(0, 50, message='Telephone must be at most 50 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Please enter email'),
        Email(message='Please enter a valid email')
    ])
    
    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_email(self, field):
        """Validate email uniqueness (exclude current user)"""
        if field.data != self.user.email and \
           User.query.filter_by(email=field.data).first():
            raise ValidationError('This email is already registered')
