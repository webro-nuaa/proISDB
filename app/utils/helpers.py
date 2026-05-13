# -*- coding: utf-8 -*-
"""
Utility functions and helpers
"""
import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                   {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'})
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder=None, max_size=None):
    """Save uploaded file"""
    if upload_folder is None:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
    
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate safe filename
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")
    
    # Generate unique filename
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_filename = f"{secrets.token_hex(16)}.{file_ext}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save file
    file.save(file_path)
    
    return file_path, unique_filename

def save_image(file, upload_folder=None, max_size=(800, 600)):
    """Save and process image file"""
    if upload_folder is None:
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'images')
    
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate safe filename
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")
    
    # Generate unique filename
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
    unique_filename = f"{secrets.token_hex(16)}.{file_ext}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Process image
    try:
        image = Image.open(file.stream)
        
        # Convert to RGB mode (remove transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode in ('RGBA', 'LA'):
                background.paste(image, mask=image.split()[-1])
                image = background
        
        # Resize
        if max_size:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save image
        image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        return file_path, unique_filename
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise ValueError(f"Image processing failed: {str(e)}")

def format_file_size(size_bytes):
    """Format file size"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def truncate_text(text, length=100, suffix='...'):
    """Truncate text"""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix

def get_client_ip(request):
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def escape_like(value):
    if not value:
        return value
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

def slugify(text):
    """Convert text to URL-friendly slug"""
    import re
    import unicodedata
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters, keep alphanumeric, hyphens, underscores
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace spaces and consecutive hyphens/underscores with single hyphen
    text = re.sub(r'[\s_-]+', '-', text)
    
    # Strip leading/trailing hyphens
    text = text.strip('-')
    
    return text

def paginate_query(query, page, per_page, error_out=False):
    """Paginate query helper"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=error_out
    )

def safe_int(value, default=0):
    """Safely convert to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safely convert to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def generate_random_string(length=16):
    """Generate random string"""
    return secrets.token_urlsafe(length)

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_html(text):
    """Clean HTML tags"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def highlight_search_terms(text, terms, max_length=200):
    """高亮搜索词并Truncate text"""
    if not text or not terms:
        return truncate_text(text, max_length)
    
    import re
    
    # Create regex for search terms
    pattern = '|'.join(re.escape(term) for term in terms if term.strip())
    if not pattern:
        return truncate_text(text, max_length)
    
    # Find first match position
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 50)
        end = min(len(text), start + max_length)
        snippet = text[start:end]
        
        # Highlight matched terms
        highlighted = re.sub(
            f'({pattern})',
            r'<mark>\1</mark>',
            snippet,
            flags=re.IGNORECASE
        )
        
        # Add ellipsis
        if start > 0:
            highlighted = '...' + highlighted
        if end < len(text):
            highlighted = highlighted + '...'
        
        return highlighted
    
    return truncate_text(text, max_length)
