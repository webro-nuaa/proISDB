# -*- coding: utf-8 -*-
"""
Article image association model
"""
from datetime import datetime, timezone
from app import db

class ArticleImage(db.Model):
    """Article image association table"""
    __tablename__ = 'article_images'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('knowledge_articles.id', ondelete='CASCADE'), nullable=False, index=True)
    image_path = db.Column(db.String(500), nullable=False, comment='图片相对路径（相对于static目录）')
    filename = db.Column(db.String(255), nullable=False, comment='文件名')
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), comment='上传时间')
    
    def __repr__(self):
        return f'<ArticleImage {self.filename} for Article {self.article_id}>'
