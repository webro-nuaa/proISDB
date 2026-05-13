# -*- coding: utf-8 -*-
"""
Knowledge Base Related Forms
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError
from wtforms.widgets import TextArea

def safe_int_coerce(value):
    """Safe integer coercion"""
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

class CategoryForm(FlaskForm):
    """Knowledge Category Form"""
    
    name = StringField('Category Name', validators=[
        DataRequired(message='Please enter category name'),
        Length(1, 100, message='Category name length should be between 1-100 characters')
    ])
    
    description = TextAreaField('Category Description', validators=[
        Length(0, 500, message='Category description length cannot exceed 500 characters')
    ])
    
    parent_id = SelectField('Parent Category', coerce=safe_int_coerce, validators=[Optional()])
    
    sort_order = StringField('Sort Order', validators=[Optional()])
    
    is_active = BooleanField('Active', default=True)
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        # Dynamically load category options
        from app.models import KnowledgeCategory
        categories = KnowledgeCategory.query.filter_by(is_active=True).all()
        choices = [('', 'None (Top Level Category)')]
        for category in categories:
            choices.append((category.id, category.name))
        self.parent_id.choices = choices

class ArticleForm(FlaskForm):
    """Article Form"""
    
    title = StringField('Article Title', validators=[
        DataRequired(message='Please enter article title'),
        Length(1, 200, message='Article title length should be between 1-200 characters')
    ])
    
    slug = StringField('URL Slug (leave empty to auto-generate)', validators=[
        Optional(),
        Length(0, 200, message='URL slug length cannot exceed 200 characters')
    ])
    
    summary = TextAreaField('Article Summary', validators=[
        Length(0, 500, message='Article summary length cannot exceed 500 characters')
    ])
    
    content = StringField('Article Content', validators=[
        DataRequired(message='Please enter article content'),
        Length(10, 50000, message='Article content length should be between 10-50000 characters')
    ], widget=TextArea())
    
    featured_image = StringField('Featured Image URL', validators=[
        Optional(),
        URL(message='Please enter a valid image URL'),
        Length(0, 500, message='Image URL length cannot exceed 500 characters')
    ])
    
    status = SelectField('Publish Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft')
    
    is_featured = BooleanField('Featured Article', default=False)
    
    meta_keywords = StringField('SEO Keywords', validators=[
        Length(0, 500, message='Keywords length cannot exceed 500 characters')
    ])
    
    meta_description = StringField('SEO Description', validators=[
        Length(0, 500, message='SEO description length cannot exceed 500 characters')
    ])
    
    tags = StringField('Tags', validators=[
        Length(0, 200, message='Tags length cannot exceed 200 characters')
    ])
    

    
    def validate_slug(self, field):
        """Validate URL slug uniqueness"""
        from app.models import KnowledgeArticle
        article = KnowledgeArticle.query.filter_by(slug=field.data).first()
        if article and (not hasattr(self, 'article_id') or article.id != self.article_id):
            raise ValidationError('This URL slug is already in use, please choose another one')

class TagForm(FlaskForm):
    """Tag Form"""
    
    name = StringField('Tag Name', validators=[
        DataRequired(message='Please enter tag name'),
        Length(1, 50, message='Tag name length should be between 1-50 characters')
    ])
    
    color = StringField('Tag Color', validators=[
        Length(7, 7, message='Please enter a valid color code (e.g., #007bff)')
    ], default='#007bff')

class SearchArticleForm(FlaskForm):
    """Article Search Form"""
    
    query = StringField('Search Keywords', validators=[
        Length(0, 200, message='Search keywords length cannot exceed 200 characters')
    ])
    
    status = SelectField('Publish Status', choices=[
        ('', 'All'),
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='')
