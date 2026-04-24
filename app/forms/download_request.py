# -*- coding: utf-8 -*-
"""
Download request form
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length, Optional
from app.models import User

class DownloadRequestForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message='Please enter first name'), Length(1, 50, message='First name must be 1-50 characters')])
    last_name = StringField('Last Name', validators=[DataRequired(message='Please enter last name'), Length(1, 50, message='Last name must be 1-50 characters')])
    institution = StringField('Institution', validators=[DataRequired(message='Please enter institution'), Length(1, 200, message='Institution must be 1-200 characters')])
    department = StringField('Department', validators=[Optional(), Length(max=200)])
    country = StringField('Country', validators=[DataRequired(message='Please enter country'), Length(1, 100, message='Country must be 1-100 characters')])
    email = StringField('Email', validators=[DataRequired(message='Please enter email'), Email(message='Please enter a valid email')])
    assigned_admin = SelectField('Assign to admin', coerce=int, validators=[DataRequired(message='Please select admin')])
    format = RadioField('Export Format', 
                       choices=[('csv', 'CSV (Spreadsheet)'), ('fasta', 'FASTA (Sequence)')],
                       default='csv',
                       validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired(message='Please enter reason'), Length(min=10, max=2000, message='Reason must be 10-2000 characters')])
