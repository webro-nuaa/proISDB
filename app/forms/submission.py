# -*- coding: utf-8 -*-
"""
数据提交相关表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email

class ISElementSubmissionForm(FlaskForm):
    """IS element submission form"""
    
    # Personal Information
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
    
    postal_address = StringField('Postal Address', validators=[
        Optional(),
        Length(0, 300, message='Postal address must be at most 300 characters')
    ])
    
    postal_code = StringField('Postal Code', validators=[
        Optional(),
        Length(0, 20, message='Postal code must be at most 20 characters')
    ])
    
    country = StringField('Country', validators=[
        DataRequired(message='Please enter country'),
        Length(1, 100, message='Country must be 1-100 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Please enter email'),
        Email(message='Please enter a valid email'),
        Length(1, 200, message='Email must be 1-200 characters')
    ])
    
    telephone = StringField('Telephone', validators=[
        Optional(),
        Length(0, 50, message='Telephone must be at most 50 characters')
    ])
    
    # IS Basic Information
    name = StringField('IS Name', validators=[
        DataRequired(message='Please enter IS name'),
        Length(1, 100, message='Name must be 1-100 characters')
    ])
    
    family = StringField('IS Family', validators=[
        DataRequired(message='Please enter IS family'),
        Length(1, 100, message='IS family must be 1-100 characters')
    ])
    
    group = StringField('IS Group', validators=[
        Optional(),
        Length(0, 100, message='Group name must be at most 100 characters')
    ])
    
    mge_type = StringField('MGE Type', validators=[
        Optional(),
        Length(0, 100, message='MGE Type must be at most 100 characters')
    ])
    
    host = StringField('Host', validators=[
        DataRequired(message='Please enter host information'),
        Length(1, 200, message='Host must be 1-200 characters')
    ])
    
    accession_number = StringField('Accession', validators=[
        Length(0, 100, message='Accession must be at most 100 characters')
    ])
    
    origin = StringField('Origin', validators=[
        Length(0, 200, message='Origin must be at most 200 characters')
    ])
    
    transposition = StringField('Transposition', validators=[
        Length(0, 100, message='Transposition must be at most 100 characters')
    ])
    
    # Length Information
    is_length = IntegerField('IS Length (bp)', validators=[
        Optional(),
        NumberRange(min=1, message='Length must be greater than 0')
    ])
    
    # Sequence Information
    left_flank = StringField('Left Flank', validators=[
        Length(0, 50, message='Left flank must be at most 50 characters')
    ])
    
    le_cleavage_site = StringField('LE Cleavage Site', validators=[
        Length(0, 100, message='LE cleavage site must be at most 100 characters')
    ])
    
    right_flank = StringField('Right Flank', validators=[
        Length(0, 50, message='Right flank must be at most 50 characters')
    ])
    
    re_cleavage_site = StringField('RE Cleavage Site', validators=[
        Length(0, 100, message='RE cleavage site must be at most 100 characters')
    ])
    
    is_sequence = TextAreaField('IS Sequence', validators=[
        Length(0, 10000, message='IS sequence must be at most 10000 characters')
    ])
    
    # ORF Information
    orf_number = IntegerField('ORF Number', validators=[
        Optional(),
        NumberRange(min=0, message='ORF number cannot be negative')
    ])
    
    # ORF1 Fields
    orf_1 = IntegerField('ORF 1', validators=[Optional()])
    orf_1_length = IntegerField('ORF 1 Length', validators=[Optional()])
    orf_1_begin = IntegerField('ORF 1 Begin', validators=[Optional()])
    orf_1_end = IntegerField('ORF 1 End', validators=[Optional()])
    orf_1_strand = StringField('ORF 1 Strand', validators=[Length(0, 64)])
    fusion_orf_1 = StringField('Fusion ORF 1', validators=[Length(0, 64)])
    orf_1_function = StringField('ORF 1 Function', validators=[Length(0, 64)])
    orf_1_chemistry = StringField('ORF 1 Chemistry', validators=[Length(0, 64)])
    orf_1_sequence = TextAreaField('ORF 1 Sequence', validators=[Length(0, 254)])
    
    # ORF2 Fields
    orf_2 = IntegerField('ORF 2', validators=[Optional()])
    orf_2_length = IntegerField('ORF 2 Length', validators=[Optional()])
    orf_2_begin = IntegerField('ORF 2 Begin', validators=[Optional()])
    orf_2_end = IntegerField('ORF 2 End', validators=[Optional()])
    orf_2_strand = StringField('ORF 2 Strand', validators=[Length(0, 64)])
    fusion_orf_2 = StringField('Fusion ORF 2', validators=[Length(0, 64)])
    orf_2_function = StringField('ORF 2 Function', validators=[Length(0, 64)])
    orf_2_chemistry = StringField('ORF 2 Chemistry', validators=[Length(0, 64)])
    orf_2_sequence = TextAreaField('ORF 2 Sequence', validators=[Length(0, 10000)])
    
    # Short name fields
    orf1 = StringField('ORF1 (Short Name)', validators=[Length(0, 64)])
    orf2 = StringField('ORF2 (Short Name)', validators=[Length(0, 64)])
    
    # TAM and other structural fields
    tam = StringField('TAM', validators=[Length(0, 64)])
    synomyns = StringField('Synonyms', validators=[Length(0, 255)])
    iso = StringField('ISO (Short Name)', validators=[Length(0, 255)])
    related_element_s = StringField('Related Elements', validators=[Length(0, 255)])
    isoform = StringField('Isoform', validators=[Length(0, 255)])
    
    length = IntegerField('Length', validators=[Optional()])
    
    # Other Information
    comment = TextAreaField('Comment', validators=[
        Length(0, 1000, message='Comment must be at most 1000 characters')
    ])
    
    references = TextAreaField('References', validators=[
        Length(0, 1000, message='References must be at most 1000 characters')
    ])
    
    # Submission Reason (stored in submission_history, not is_elements)
    submission_reason = TextAreaField('Submission Reason', validators=[
        Optional(),
        Length(0, 500, message='Submission reason must be at most 500 characters')
    ])

class ReviewForm(FlaskForm):
    """Review form"""
    
    status = SelectField('Review Decision', validators=[
        DataRequired(message='Please select review decision')
    ], choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    
    review_notes = TextAreaField('Review Notes', validators=[
        Optional(),
        Length(0, 1000, message='Review notes must be at most 1000 characters')
    ])

class AdminISElementForm(FlaskForm):
    """Admin IS element form - without submitter info requirements"""
    
    # IS Basic Information - Only name and family are required
    name = StringField('IS Name', validators=[
        DataRequired(message='Please enter IS name'),
        Length(1, 100, message='Name must be 1-100 characters')
    ])
    
    family = StringField('IS Family', validators=[
        Optional(),
        Length(0, 100, message='IS family must be at most 100 characters')
    ])
    
    group = StringField('IS Group', validators=[
        Optional(),
        Length(0, 100, message='Group name must be at most 100 characters')
    ])
    
    mge_type = StringField('MGE Type', validators=[
        Optional(),
        Length(0, 100, message='MGE Type must be at most 100 characters')
    ])
    
    host = StringField('Host', validators=[
        Optional(),
        Length(0, 200, message='Host must be at most 200 characters')
    ])
    
    accession_number = StringField('Accession', validators=[
        Optional(),
        Length(0, 100, message='Accession must be at most 100 characters')
    ])
    
    origin = StringField('Origin', validators=[
        Optional(),
        Length(0, 200, message='Origin must be at most 200 characters')
    ])
    
    transposition = StringField('Transposition', validators=[
        Optional(),
        Length(0, 100, message='Transposition must be at most 100 characters')
    ])
    
    # Length Information
    is_length = IntegerField('IS Length (bp)', validators=[
        Optional(),
        NumberRange(min=1, message='Length must be greater than 0')
    ])
    
    # Sequence Information (left_flank and right_flank are auto-calculated @property, not form fields)
    le_cleavage_site = StringField('LE Cleavage Site', validators=[
        Optional(),
        Length(0, 100, message='LE cleavage site must be at most 100 characters')
    ])
    
    re_cleavage_site = StringField('RE Cleavage Site', validators=[
        Optional(),
        Length(0, 100, message='RE cleavage site must be at most 100 characters')
    ])
    
    is_sequence = TextAreaField('IS Sequence', validators=[
        Optional(),
        Length(0, 10000, message='IS sequence must be at most 10000 characters')
    ])
    
    # ORF Information
    orf_number = IntegerField('ORF Number', validators=[
        Optional(),
        NumberRange(min=0, message='ORF number cannot be negative')
    ])
    
    # ORF1 Fields
    orf_1 = IntegerField('ORF 1', validators=[Optional()])
    orf_1_length = IntegerField('ORF 1 Length', validators=[Optional()])
    orf_1_begin = IntegerField('ORF 1 Begin', validators=[Optional()])
    orf_1_end = IntegerField('ORF 1 End', validators=[Optional()])
    orf_1_strand = StringField('ORF 1 Strand', validators=[Optional(), Length(0, 64)])
    fusion_orf_1 = StringField('Fusion ORF 1', validators=[Optional(), Length(0, 64)])
    orf_1_function = StringField('ORF 1 Function', validators=[Optional(), Length(0, 64)])
    orf_1_chemistry = StringField('ORF 1 Chemistry', validators=[Optional(), Length(0, 64)])
    orf_1_sequence = TextAreaField('ORF 1 Sequence', validators=[Optional(), Length(0, 254)])
    
    # ORF2 Fields
    orf_2 = IntegerField('ORF 2', validators=[Optional()])
    orf_2_length = IntegerField('ORF 2 Length', validators=[Optional()])
    orf_2_begin = IntegerField('ORF 2 Begin', validators=[Optional()])
    orf_2_end = IntegerField('ORF 2 End', validators=[Optional()])
    orf_2_strand = StringField('ORF 2 Strand', validators=[Optional(), Length(0, 64)])
    fusion_orf_2 = StringField('Fusion ORF 2', validators=[Optional(), Length(0, 64)])
    orf_2_function = StringField('ORF 2 Function', validators=[Optional(), Length(0, 64)])
    orf_2_chemistry = StringField('ORF 2 Chemistry', validators=[Optional(), Length(0, 64)])
    orf_2_sequence = TextAreaField('ORF 2 Sequence', validators=[Optional(), Length(0, 10000)])
    
    # Short name fields
    orf1 = StringField('ORF1 (Short Name)', validators=[Optional(), Length(0, 64)])
    orf2 = StringField('ORF2 (Short Name)', validators=[Optional(), Length(0, 64)])
    
    # TAM and other structural fields
    tam = StringField('TAM', validators=[Optional(), Length(0, 64)])
    synomyns = StringField('Synonyms', validators=[Optional(), Length(0, 255)])
    iso = StringField('ISO (Short Name)', validators=[Optional(), Length(0, 255)])
    related_element_s = StringField('Related Elements', validators=[Optional(), Length(0, 255)])
    isoform = StringField('Isoform', validators=[Optional(), Length(0, 255)])
    
    length = IntegerField('Length', validators=[Optional()])
    
    # Other Information
    comment = TextAreaField('Comment', validators=[
        Optional(),
        Length(0, 1000, message='Comment must be at most 1000 characters')
    ])
    
    references = TextAreaField('References', validators=[
        Optional(),
        Length(0, 1000, message='References must be at most 1000 characters')
    ])

