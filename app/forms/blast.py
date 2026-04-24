# -*- coding: utf-8 -*-
"""
BLAST Forms
"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class BlastSearchForm(FlaskForm):
    """BLAST Search Form"""
    
    sequence = TextAreaField(
        'Sequence',
        validators=[
            DataRequired(message='Please enter a query sequence'),
            Length(min=10, message='Sequence must be at least 10 bases long')
        ],
        render_kw={
            'class': 'form-control font-monospace',
            'rows': 10,
            'placeholder': 'Enter FASTA format sequence or plain sequence:\n>Query_Sequence\nATGCGATCGATCGATCGATC...\n\nOr enter sequence directly (without >header):\nATGCGATCGATCGATCGATC...'
        }
    )
    
    blast_type = SelectField(
        'BLAST Type',
        choices=[
            ('blastn', 'blastn - Nucleotide sequence alignment'),
            ('blastp', 'blastp - Protein sequence alignment')
        ],
        default='blastn',
        render_kw={'class': 'form-select'}
    )
    
    evalue = SelectField(
        'E-value Threshold',
        choices=[
            ('10', '10 - Standard (recommended)'),
            ('1', '1 - Moderate stringency'),
            ('0.1', '0.1 - High stringency'),
            ('0.01', '0.01 - Very high stringency'),
            ('0.001', '0.001 - Strict'),
            ('0.0001', '0.0001 - Very strict'),
            ('100', '100 - Relaxed'),
            ('1000', '1000 - Very relaxed')
        ],
        default='10',
        render_kw={'class': 'form-select'}
    )
    
    max_hits = SelectField(
        'Max Results',
        choices=[
            ('10', '10'),
            ('20', '20'),
            ('50', '50 (recommended)'),
            ('100', '100'),
            ('200', '200'),
            ('500', '500')
        ],
        default='50',
        render_kw={'class': 'form-select'}
    )
    
    word_size = SelectField(
        'Word Size',
        choices=[
            ('11', '11 - Standard (recommended)'),
            ('7', '7 - Short sequences'),
            ('15', '15 - High similarity'),
            ('20', '20 - Very high similarity')
        ],
        default='11',
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'BLAST Search',
        render_kw={'class': 'btn btn-primary btn-lg'}
    )
