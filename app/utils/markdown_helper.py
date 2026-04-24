# -*- coding: utf-8 -*-
"""
Markdown处理工具
"""
import re
import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
from pygments.formatters import HtmlFormatter


class MarkdownProcessor:
    """Markdown处理器"""
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',      # 代码高亮
                'toc',             # 目录生成
                'tables',          # 表格支持
                'fenced_code',     # 围栏代码块
                'nl2br',           # 换行转换
                'attr_list',       # 属性列表
                'def_list',        # 定义列表
                'abbr',            # 缩写
                'footnotes',       # 脚注
                'admonition',      # 警告框
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
        将Markdown文本转换为HTML
        
        Args:
            text (str): Markdown文本
            
        Returns:
            dict: 包含html内容和目录的字典
        """
        if not text:
            return {'html': '', 'toc': ''}
        
        # 重置Markdown处理器
        self.md.reset()
        
        # 转换Markdown到HTML
        html = self.md.convert(text)
        
        # 获取目录
        toc = getattr(self.md, 'toc', '')
        
        # 后处理HTML
        html = self._post_process_html(html)
        
        return {
            'html': html,
            'toc': toc
        }
    
    def _post_process_html(self, html):
        """
        后处理HTML内容
        
        Args:
            html (str): 原始HTML
            
        Returns:
            str: 处理后的HTML
        """
        # 为图片添加响应式类
        html = re.sub(
            r'<img([^>]*?)>',
            r'<img\1 class="img-fluid rounded shadow-sm">',
            html
        )
        
        # 为表格添加Bootstrap样式
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
        
        # 为链接添加外部链接标识
        html = re.sub(
            r'<a href="(https?://[^"]*)"([^>]*?)>',
            r'<a href="\1"\2 target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt me-1"></i>',
            html
        )
        
        # 为引用块添加样式
        html = re.sub(
            r'<blockquote>',
            r'<blockquote class="blockquote border-start border-primary border-3 ps-3 text-muted">',
            html
        )
        
        # 为警告框添加Bootstrap样式
        html = self._process_admonitions(html)
        
        return html
    
    def _process_admonitions(self, html):
        """
        处理警告框/提示框
        
        Args:
            html (str): 原始HTML
            
        Returns:
            str: 处理后的HTML
        """
        # 定义警告框类型映射
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
        从Markdown文本中提取纯文本摘要
        
        Args:
            markdown_text (str): Markdown文本
            max_length (int): 最大长度
            
        Returns:
            str: 纯文本摘要
        """
        if not markdown_text:
            return ''
        
        # 转换为HTML然后提取纯文本
        html = self.md.convert(markdown_text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', html)
        
        # 清理空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 截断文本
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text
    
    @staticmethod
    def get_css():
        """
        获取代码高亮的CSS样式
        
        Returns:
            str: CSS样式字符串
        """
        formatter = HtmlFormatter(style='github', noclasses=False)
        return formatter.get_style_defs('.highlight')


# 全局实例
markdown_processor = MarkdownProcessor()
