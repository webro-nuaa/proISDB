# -*- coding: utf-8 -*-
"""
视图包
"""

# 这里可以导入所有的蓝图
from .main import main
from .auth import auth
from .search import search

__all__ = ['main', 'auth', 'search']