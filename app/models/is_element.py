# -*- coding: utf-8 -*-
"""
IS Element model
"""
from datetime import datetime, timezone
from app import db

class ISElement(db.Model):
    """IS Element model"""
    __tablename__ = 'is_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    # Core fields
    name = db.Column(db.String(64), nullable=False, comment='IS元素名称')
    family = db.Column(db.String(64), nullable=False, comment='IS家族')
    # Map to database column `group`
    group = db.Column('group', db.String(64), comment='IS组')
    mge_type = db.Column(db.String(64), comment='MGE类型')
    related_element_s = db.Column(db.String(255), comment='相关元素')
    isoform = db.Column(db.String(255), comment='同型')
    # Standard synonyms column
    synomyns = db.Column('synomyns', db.String(255), comment='标准同义词')
    # Short name / iso column (present in SQL)
    iso = db.Column('iso', db.String(255), comment='短名 / iso')
    # Additional/extension fields per latest schema
    accession_number = db.Column(db.String(64), comment='登录号')
    transposition = db.Column(db.String(255), comment='转座情况')
    origin = db.Column(db.String(80), comment='来源')
    host = db.Column(db.String(64), comment='宿主')
    is_length = db.Column(db.Integer, comment='IS长度')
    # left_flank/right_flank are not explicit columns in the current schema.
    # Retain as read-only @property, inferred from is_sequence if available.
    # Cleavage sites exist as explicit columns.
    le_cleavage_site = db.Column(db.String(64), comment='LE切割位点')
    re_cleavage_site = db.Column(db.String(64), comment='RE切割位点')
    tam = db.Column(db.String(64), comment='TAM')

    @property
    def left_flank(self):
        seq = getattr(self, 'is_sequence', None)
        if seq:
            return seq[:50]
        return None

    @property
    def right_flank(self):
        seq = getattr(self, 'is_sequence', None)
        if seq:
            return seq[-50:]
        return None
    # Sequence fields
    is_sequence = db.Column(db.Text, comment='IS序列')
    orf_number = db.Column(db.Integer, comment='ORF数量')
    # Legacy simple ORF / length fields
    length = db.Column(db.Integer, comment='长度')
    # Detailed ORF fields from schema
    orf_1 = db.Column(db.Integer, comment='ORF 1')
    orf_1_length = db.Column(db.Integer, comment='ORF 1 长度')
    orf_1_begin = db.Column(db.Integer, comment='ORF 1 开始')
    orf_1_end = db.Column(db.Integer, comment='ORF 1 结束')
    orf_1_strand = db.Column(db.String(64), comment='ORF 1 链方向')
    fusion_orf_1 = db.Column('fusion_orf_1', db.String(64), comment='融合 ORF 1')
    orf_1_function = db.Column(db.String(64), comment='ORF 1 功能')
    orf_1_chemistry = db.Column(db.String(64), comment='ORF 1 Chemistry')
    orf_1_sequence = db.Column(db.String(254), comment='ORF 1 序列')
    orf_2 = db.Column(db.Integer, comment='ORF 2')
    orf_2_length = db.Column(db.Integer, comment='ORF 2 长度')
    orf_2_begin = db.Column(db.Integer, comment='ORF 2 开始')
    orf_2_end = db.Column(db.Integer, comment='ORF 2 结束')
    orf_2_strand = db.Column(db.String(64), comment='ORF 2 链方向')
    fusion_orf_2 = db.Column(db.String(64), comment='融合 ORF 2')
    orf_2_function = db.Column(db.String(64), comment='ORF 2 功能')
    orf_2_chemistry = db.Column(db.String(64), comment='ORF 2 Chemistry')
    orf_2_sequence = db.Column(db.Text, comment='ORF 2 序列')
    # Both orf1/orf2 (varchar) and orf_1/orf_2 (int) exist; keep both
    orf1 = db.Column('orf1', db.String(64), comment='ORF1 (短名)')
    orf2 = db.Column('orf2', db.String(64), comment='ORF2 (短名)')
    # comment/references use Text for larger content
    comment = db.Column(db.Text, comment='备注')
    references = db.Column(db.Text, comment='参考文献')
    
    # Submitter personal info
    submitter_first_name = db.Column(db.String(50), comment='提交者姓')
    submitter_last_name = db.Column(db.String(50), comment='提交者名')
    submitter_institution = db.Column(db.String(200), comment='提交者机构')
    submitter_department = db.Column(db.String(200), comment='提交者部门')
    submitter_postal_address = db.Column(db.String(300), comment='提交者邮政地址')
    submitter_postal_code = db.Column(db.String(20), comment='提交者邮政编码')
    submitter_country = db.Column(db.String(100), comment='提交者国家')
    submitter_email = db.Column(db.String(200), comment='提交者电子邮箱')
    submitter_telephone = db.Column(db.String(50), comment='提交者电话')
    
    # Data management fields
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), 
                      default='pending', comment='审核状态')
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='提交者ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审核者ID')
    submission_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), comment='提交时间')
    review_date = db.Column(db.DateTime, comment='审核时间')
    review_comment = db.Column(db.Text, comment='审核意见')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships defined via User model backrefs
    submission_histories = db.relationship('SubmissionHistory', backref='is_element', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ISElement {self.name}>'
    
    @classmethod
    def search(cls, query_text, family=None, host=None, status='approved', page=1, per_page=20):
        """搜索IS元素"""
        query = cls.query.filter_by(status=status)
        
        if query_text:
            # 全文搜索
            search_filter = db.or_(
                cls.name.contains(query_text),
                cls.family.contains(query_text),
                cls.host.contains(query_text),
                cls.comment.contains(query_text)
            )
            query = query.filter(search_filter)
        
        if family:
            query = query.filter_by(family=family)
        
        if host:
            query = query.filter(cls.host.contains(host))
        
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def get_families(cls):
        """获取所有IS家族"""
        return db.session.query(cls.family).distinct().all()
    
    @classmethod
    def get_hosts(cls):
        """获取所有宿主"""
        return db.session.query(cls.host).distinct().all()
    
    def to_dict(self, include_sequences=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'family': self.family,
            'group': self.group,
            'synonyms': getattr(self, 'synonyms', None),
            'mge_type': self.mge_type,
            'accession_number': self.accession_number,
            'host': self.host,
            'is_length': self.is_length,
            'status': self.status,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'comment': self.comment
        }
        
        if include_sequences:
            data.update({
                'is_sequence': self.is_sequence,
                'left_flank': self.left_flank,
                'right_flank': self.right_flank,
                'le_cleavage_site': self.le_cleavage_site,
                're_cleavage_site': self.re_cleavage_site
            })
        
        return data
