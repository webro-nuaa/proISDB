# -*- coding: utf-8 -*-
"""
Markdown processing utility
"""
import re
import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
from pygments.formatters import HtmlFormatter


class MarkdownProcessor:
    """Markdown processor"""
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',      # Code highlighting
                'toc',             # Table of contents
                'tables',          # Table support
                'fenced_code',     # Fenced code blocks
                'nl2br',           # Line break conversion
                'attr_list',       # Attribute lists
                'def_list',        # Definition lists
                'abbr',            # Abbreviations
                'footnotes',       # Footnotes
                'admonition',      # Admonitions
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                    'noclasses': False,
                },
                'toc': {
                    'permalink': False,
                    'permalink_title': '链接到此标题',
                    'toc_depth': 6,
                }
            }
        )
    
    def convert(self, text):
        """
        Convert Markdown text to HTML
        
        Args:
            text (str): Markdown文本
            
        Returns:
            dict: 包含html内容和目录的字典
        """
        if not text:
            return {'html': '', 'toc': ''}
        
        # 重置Markdown processor
        self.md.reset()
        
        # 转换Markdown到HTML
        html = self.md.convert(text)
        
        # Extract TOC
        toc = getattr(self.md, 'toc', '')
        
        # Post-process HTML
        html = self._post_process_html(html)
        
        return {
            'html': html,
            'toc': toc
        }
    
    def _post_process_html(self, html):
        """
        Post-process HTML内容
        
        Args:
            html (str): 原始HTML
            
        Returns:
            str: 处理后的HTML
        """
        # Add responsive class to images
        html = re.sub(
            r'<img([^>]*?)>',
            r'<img\1 class="img-fluid rounded shadow-sm">',
            html
        )
        
        # Add Bootstrap styles to tables
        html = re.sub(
            r'<table>',
            r'<div class="table-responsive"><table class="table table-striped table-hover">',
            html
        )
        html = re.sub(
            r'</table>',
            r'</table></div>',
            html
        )
        
        # Add external link indicator
        html = re.sub(
            r'<a href="(https?://[^"]*)"([^>]*?)>',
            r'<a href="\1"\2 target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt me-1"></i>',
            html
        )
        
        # Add blockquote styles
        html = re.sub(
            r'<blockquote>',
            r'<blockquote class="blockquote border-start border-primary border-3 ps-3 text-muted">',
            html
        )
        
        # 为Admonitions添加Bootstrap样式
        html = self._process_admonitions(html)
        
        return html
    
    def _process_admonitions(self, html):
        """
        处理Admonitions/提示框
        
        Args:
            html (str): 原始HTML
            
        Returns:
            str: 处理后的HTML
        """
        # 定义Admonitions类型映射
        admonition_map = {
            'note': ('info', 'info-circle'),
            'tip': ('success', 'lightbulb'),
            'info': ('info', 'info-circle'),
            'warning': ('warning', 'exclamation-triangle'),
            'danger': ('danger', 'exclamation-triangle'),
            'error': ('danger', 'times-circle'),
            'success': ('success', 'check-circle'),
        }
        
        for adm_type, (bs_class, icon) in admonition_map.items():
            pattern = rf'<div class="admonition {adm_type}">\s*<p class="admonition-title">(.*?)</p>(.*?)</div>'
            replacement = (
                f'<div class="alert alert-{bs_class} d-flex align-items-start" role="alert">'
                f'<i class="fas fa-{icon} me-2 mt-1"></i>'
                f'<div><strong>\\1</strong>\\2</div>'
                f'</div>'
            )
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)
        
        return html
    
    def get_text_summary(self, markdown_text, max_length=200):
        """
        Extract plain text summary from Markdown
        
        Args:
            markdown_text (str): Markdown文本
            max_length (int): 最大长度
            
        Returns:
            str: 纯文本摘要
        """
        if not markdown_text:
            return ''
        
        # Convert to HTML then extract plain text
        html = self.md.convert(markdown_text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate text
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text
    
    @staticmethod
    def get_css():
        """
        获取Code highlighting的CSS样式
        
        Returns:
            str: CSS样式字符串
        """
        formatter = HtmlFormatter(style='github', noclasses=False)
        return formatter.get_style_defs('.highlight')


# Global instance
markdown_processor = MarkdownProcessor()
