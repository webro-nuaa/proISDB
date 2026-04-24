# -*- coding: utf-8 -*-
"""
工具函数和辅助方法
"""
import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名是否允许"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                   {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'})
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder=None, max_size=None):
    """保存上传的文件"""
    if upload_folder is None:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
    
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")
    
    # 生成唯一文件名
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_filename = f"{secrets.token_hex(16)}.{file_ext}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # 保存文件
    file.save(file_path)
    
    return file_path, unique_filename

def save_image(file, upload_folder=None, max_size=(800, 600)):
    """保存并处理图片文件"""
    if upload_folder is None:
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'images')
    
    os.makedirs(upload_folder, exist_ok=True)
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")
    
    # 生成唯一文件名
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
    unique_filename = f"{secrets.token_hex(16)}.{file_ext}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # 处理图片
    try:
        image = Image.open(file.stream)
        
        # 转换为RGB模式（去除透明度）
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode in ('RGBA', 'LA'):
                background.paste(image, mask=image.split()[-1])
                image = background
        
        # 调整大小
        if max_size:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 保存图片
        image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        return file_path, unique_filename
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise ValueError(f"Image processing failed: {str(e)}")

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def truncate_text(text, length=100, suffix='...'):
    """截断文本"""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix

def get_client_ip(request):
    """获取客户端IP地址"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def escape_like(value):
    if not value:
        return value
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

def slugify(text):
    """将文本转换为URL友好的slug"""
    import re
    import unicodedata
    
    # 标准化Unicode字符
    text = unicodedata.normalize('NFKD', text)
    
    # 转换为小写
    text = text.lower()
    
    # 移除特殊字符，保留字母、数字、连字符和下划线
    text = re.sub(r'[^\w\s-]', '', text)
    
    # 将空格和连续的连字符/下划线转换为单个连字符
    text = re.sub(r'[\s_-]+', '-', text)
    
    # 移除开头和结尾的连字符
    text = text.strip('-')
    
    return text

def paginate_query(query, page, per_page, error_out=False):
    """分页查询辅助函数"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=error_out
    )

def safe_int(value, default=0):
    """安全地将值转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """安全地将值转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def generate_random_string(length=16):
    """生成随机字符串"""
    return secrets.token_urlsafe(length)

def validate_email(email):
    """简单的邮箱验证"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_html(text):
    """清理HTML标签"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def highlight_search_terms(text, terms, max_length=200):
    """高亮搜索词并截断文本"""
    if not text or not terms:
        return truncate_text(text, max_length)
    
    import re
    
    # 创建搜索词的正则表达式
    pattern = '|'.join(re.escape(term) for term in terms if term.strip())
    if not pattern:
        return truncate_text(text, max_length)
    
    # 查找第一个匹配项的位置
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 50)
        end = min(len(text), start + max_length)
        snippet = text[start:end]
        
        # 高亮匹配的词
        highlighted = re.sub(
            f'({pattern})',
            r'<mark>\1</mark>',
            snippet,
            flags=re.IGNORECASE
        )
        
        # 添加省略号
        if start > 0:
            highlighted = '...' + highlighted
        if end < len(text):
            highlighted = highlighted + '...'
        
        return highlighted
    
    return truncate_text(text, max_length)
