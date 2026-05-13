# -*- coding: utf-8 -*-
"""
API views
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/')
def index():
    """API documentation home"""
    return render_template('api/index.html')

@api.route('/preview-markdown', methods=['POST'])
@login_required
def preview_markdown():
    """Markdown preview API"""
    try:
        content = request.form.get('content', '')
        if not content:
            return jsonify({
                'success': True,
                'html': '<p class="text-muted">预览区域，输入Markdown内容后显示渲染效果</p>'
            })
        
        # 使用Markdown处理器
        from app.utils.markdown_helper import markdown_processor
        result = markdown_processor.convert(content)
        
        return jsonify({
            'success': True,
            'html': result['html'],
            'toc': result.get('toc', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api.route('/families')
def get_families():
    """Get IS family list API"""
    try:
        from app.models import ISElement
        families = ISElement.get_families()
        return jsonify({
            'success': True,
            'families': [f[0] for f in families]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'families': []
        }), 500
