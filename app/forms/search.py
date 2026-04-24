# -*- coding: utf-8 -*-
"""
搜索相关表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import Length, NumberRange, Optional

class SearchForm(FlaskForm):
    """搜索表单"""
    query = StringField('搜索关键词', validators=[
        Length(0, 200, message='搜索关键词长度不能超过200个字符')
    ])
    family = SelectField('IS家族', choices=[('', '全部')], default='')
    host = StringField('宿主', validators=[
        Length(0, 200, message='宿主名称长度不能超过200个字符')
    ])
    min_length = IntegerField('最小长度', validators=[
        Optional(),
        NumberRange(min=1, message='长度必须大于0')
    ])
    max_length = IntegerField('最大长度', validators=[
        Optional(),
        NumberRange(min=1, message='长度必须大于0')
    ])
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # 动态加载IS家族选项
        from app.models import ISElement
        families = ISElement.get_families()
        self.family.choices = [('', '全部')] + [(f[0], f[0]) for f in families]

class AdvancedSearchForm(FlaskForm):
    """高级搜索表单"""
    # 搜索字段
    name = StringField('IS元素名称', validators=[
        Length(0, 100, message='名称长度不能超过100个字符')
    ])
    name_match = SelectField('名称匹配方式', choices=[
        ('contains', '包含'),
        ('begin_with', '开头匹配'),
        ('end_with', '结尾匹配'),
        ('equal_to', '完全匹配')
    ], default='contains')
    
    family = SelectField('IS家族', choices=[('', '全部')], default='')
    family_match = SelectField('家族匹配方式', choices=[
        ('contains', '包含'),
        ('begin_with', '开头匹配'),
        ('end_with', '结尾匹配'),
        ('equal_to', '完全匹配')
    ], default='contains')
    
    origin = StringField('来源', validators=[
        Length(0, 200, message='来源长度不能超过200个字符')
    ])
    origin_match = SelectField('来源匹配方式', choices=[
        ('contains', '包含'),
        ('begin_with', '开头匹配'),
        ('end_with', '结尾匹配'),
        ('equal_to', '完全匹配')
    ], default='contains')
    
    mge_type = SelectField('MGE类型', choices=[
        ('', 'All'),
        ('IS', 'IS'),
        ('MITE', 'MITE'),
        ('MIC', 'MIC'),
        ('tIS', 'tIS'),
        ('Transposon', 'Transposon')
    ], default='')
    
    group = StringField('IS组', validators=[
        Length(0, 100, message='组名长度不能超过100个字符')
    ])
    host = StringField('宿主', validators=[
        Length(0, 200, message='宿主名称长度不能超过200个字符')
    ])
    accession = StringField('登录号', validators=[
        Length(0, 100, message='登录号长度不能超过100个字符')
    ])

    group_match = SelectField('组匹配方式', choices=[
        ('contains', '包含'),
        ('begin_with', '开头匹配'),
        ('end_with', '结尾匹配'),
        ('equal_to', '完全匹配')
    ], default='contains')
    
    accession_match = SelectField('登录号匹配方式', choices=[
        ('contains', '包含'),
        ('begin_with', '开头匹配'),
        ('end_with', '结尾匹配'),
        ('equal_to', '完全匹配')
    ], default='contains')
    
    # Additional field: Length (different from min/max length)
    length_field = StringField('长度字段', validators=[
        Length(0, 50, message='长度字段长度不能超过50个字符')
    ])
    length_match = SelectField('长度字段匹配方式', choices=[
        ('equal_to', '等于'),
        ('gte', '大于等于'),
        ('lte', '小于等于')
    ], default='equal_to')
    
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        # 动态加载IS家族选项
        from app.models import ISElement
        families = ISElement.get_families()
        self.family.choices = [('', '全部')] + [(f[0], f[0]) for f in families]
