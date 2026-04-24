# -*- coding: utf-8 -*-
"""
Jinja2 模板过滤器
"""
from datetime import datetime, timezone
import re

def truncate_text(text, length=100, suffix='...'):
    """截断文本"""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix

def datetime_format(value, format='%Y-%m-%d %H:%M'):
    """格式化日期时间"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    return value.strftime(format)

def timeago(value):
    """相对时间显示"""
    if not value:
        return ''
    
    now = datetime.now(timezone.utc)
    diff = now - value
    
    if diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"

def highlight_search(text, terms):
    """高亮搜索词"""
    if not text or not terms:
        return text
    
    if isinstance(terms, str):
        terms = [terms]
    
    # 创建搜索词的正则表达式
    pattern = '|'.join(re.escape(term) for term in terms if term.strip())
    if not pattern:
        return text
    
    # 高亮匹配的词
    highlighted = re.sub(
        f'({pattern})',
        r'<mark>\1</mark>',
        text,
        flags=re.IGNORECASE
    )
    
    return highlighted

def format_file_size(size_bytes):
    """格式化文件大小"""
    if not size_bytes:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def pluralize(count, singular, plural=None):
    """复数形式"""
    if plural is None:
        plural = singular + 's'
    
    return singular if count == 1 else plural

def markdown_to_html(text):
    """完整的Markdown转HTML处理"""
    if not text:
        return ''
    
    try:
        from app.utils.markdown_helper import markdown_processor
        result = markdown_processor.convert(text)
        return result['html']
    except ImportError:
        # 回退到简单处理
        return simple_markdown_to_html(text)

def simple_markdown_to_html(text):
    """简单的Markdown转HTML（回退方案）"""
    if not text:
        return ''
    
    # 粗体
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    
    # 斜体
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # 代码
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    # 换行
    text = text.replace('\n', '<br>')
    
    return text

def markdown_to_text(text):
    """Markdown转纯文本摘要"""
    if not text:
        return ''
    
    try:
        from app.utils.markdown_helper import markdown_processor
        return markdown_processor.get_text_summary(text)
    except ImportError:
        # 回退处理
        return clean_html(simple_markdown_to_html(text))

def clean_html(text):
    """清理HTML标签"""
    if not text:
        return ''
    
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_number(value, decimal_places=0):
    """格式化数字"""
    if not isinstance(value, (int, float)):
        return value
    
    if decimal_places == 0:
        return f"{value:,}"
    else:
        return f"{value:,.{decimal_places}f}"

def status_badge(status):
    """状态徽章"""
    badges = {
        'pending': '<span class="badge bg-warning">待审核</span>',
        'approved': '<span class="badge bg-success">已通过</span>',
        'rejected': '<span class="badge bg-danger">已拒绝</span>',
        'published': '<span class="badge bg-success">已发布</span>',
        'draft': '<span class="badge bg-secondary">草稿</span>',
        'archived': '<span class="badge bg-dark">已归档</span>',
    }
    
    return badges.get(status, f'<span class="badge bg-light text-dark">{status}</span>')

def user_avatar(user, size=32):
    """用户头像"""
    if not user:
        return f'<div class="bg-secondary rounded-circle d-inline-flex align-items-center justify-content-center" style="width:{size}px;height:{size}px;"><i class="fas fa-user text-white"></i></div>'
    
    # 生成基于用户名的颜色
    import hashlib
    hash_obj = hashlib.md5(user.username.encode())
    color = hash_obj.hexdigest()[:6]
    
    initial = user.username[0].upper()
    
    return f'<div class="rounded-circle d-inline-flex align-items-center justify-content-center text-white fw-bold" style="width:{size}px;height:{size}px;background-color:#{color};">{initial}</div>'

def build_page_url(page):
    """构造当前页面新的分页URL，保留其它查询参数"""
    try:
        from flask import request, url_for
        args = request.args.to_dict()
        args['page'] = page
        # 使用当前端点（适用于 search.index）
        endpoint = request.endpoint or 'search.index'
        return url_for(endpoint, **args)
    except Exception:
        return '#'

def register_filters(app):
    """注册所有过滤器"""
    app.jinja_env.filters['truncate_text'] = truncate_text
    app.jinja_env.filters['datetime'] = datetime_format
    app.jinja_env.filters['timeago'] = timeago
    app.jinja_env.filters['highlight_search'] = highlight_search
    app.jinja_env.filters['file_size'] = format_file_size
    app.jinja_env.filters['pluralize'] = pluralize
    app.jinja_env.filters['markdown'] = markdown_to_html
    app.jinja_env.filters['markdown_text'] = markdown_to_text
    app.jinja_env.filters['clean_html'] = clean_html
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['status_badge'] = status_badge
    app.jinja_env.filters['user_avatar'] = user_avatar
    # 全局函数
    app.jinja_env.globals['page_url'] = build_page_url
