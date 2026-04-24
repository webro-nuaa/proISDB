# -*- coding: utf-8 -*-
"""
科普知识模型
"""
from datetime import datetime, timezone
from app import db

class KnowledgeCategory(db.Model):
    """知识分类模型"""
    __tablename__ = 'knowledge_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 自关联
    parent = db.relationship('KnowledgeCategory', remote_side=[id], backref='children')
    articles = db.relationship('KnowledgeArticle', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<KnowledgeCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_active': self.is_active
        }

class KnowledgeTag(db.Model):
    """知识标签模型"""
    __tablename__ = 'knowledge_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#007bff')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<KnowledgeTag {self.name}>'

# 文章标签关联表
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('knowledge_articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('knowledge_tags.id'), primary_key=True)
)

class KnowledgeArticle(db.Model):
    """科普文章模型"""
    __tablename__ = 'knowledge_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('knowledge_categories.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='draft')
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    meta_keywords = db.Column(db.String(500))
    meta_description = db.Column(db.String(500))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关联关系
    tags = db.relationship('KnowledgeTag', secondary=article_tags, 
                          backref=db.backref('articles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.title}>'
    
    @classmethod
    def search(cls, query_text, status='published', page=1, per_page=10):
        """搜索文章"""
        query = cls.query.filter_by(status=status)
        
        if query_text:
            search_filter = db.or_(
                cls.title.contains(query_text),
                cls.content.contains(query_text),
                cls.summary.contains(query_text)
            )
            query = query.filter(search_filter)
        
        return query.order_by(cls.published_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @classmethod
    def get_featured(cls, limit=5):
        """获取推荐文章"""
        return cls.query.filter_by(status='published', is_featured=True)\
                       .order_by(cls.published_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent(cls, limit=10):
        """获取最新文章"""
        return cls.query.filter_by(status='published')\
                       .order_by(cls.published_at.desc())\
                       .limit(limit).all()
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
    def to_dict(self, include_content=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'featured_image': self.featured_image,
            'category_id': self.category_id,
            'author_id': self.author_id,
            'status': self.status,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'is_featured': self.is_featured,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'tags': [tag.name for tag in self.tags]
        }
        
        if include_content:
            data['content'] = self.content
        
        return data
