# -*- coding: utf-8 -*-
"""Tests for models not covered in other test files."""
import pytest
from datetime import datetime, timezone
from app.models import (
    User, ISElement, KnowledgeArticle, KnowledgeCategory, KnowledgeTag,
    SystemConfig, SearchLog, PageView, AdminLog,
    SubmissionHistory, BatchImport,
    EmailVerification, DownloadRequest, DownloadRequestItem,
    ArticleImage
)


class TestBatchImportModel:

    def test_create(self, db):
        imp = BatchImport(
            filename='test.csv', original_filename='test.csv',
            total_records=100, imported_by=1
        )
        db.session.add(imp)
        db.session.commit()
        assert imp.status == 'processing'
        assert imp.total_records == 100

    def test_repr(self, db):
        imp = BatchImport(filename='f.csv', original_filename='f.csv', total_records=1, imported_by=1)
        assert repr(imp) == '<BatchImport f.csv>'


class TestPageViewModel:

    def test_log_view(self, db):
        view = PageView.log_view(page_type='home')
        assert view.page_type == 'home'

    def test_log_view_with_user(self, db, test_user):
        view = PageView.log_view(page_type='search', user=test_user, request=None)
        assert view.page_type == 'search'
        assert view.user_id == test_user.id

    def test_flush_pending(self, db):
        """Test that pending views get flushed."""
        PageView._pending_views.clear()
        for i in range(10):
            PageView.log_view(page_type='home')
        # After 10 views, they should be flushed
        assert len(PageView._pending_views) == 0


class TestEmailVerificationModel:

    def test_create(self, db):
        ver = EmailVerification(
            user_id=1, email='test@example.com',
            purpose='email_change', validity_minutes=15
        )
        db.session.add(ver)
        db.session.commit()
        assert ver.id is not None
        assert ver.is_verified is False
        assert ver.verification_code is not None

    def test_verify_success(self, db):
        from datetime import datetime, timezone
        ver = EmailVerification(
            user_id=1, email='test@example.com',
            purpose='email_change', validity_minutes=15
        )
        db.session.add(ver)
        db.session.commit()

        success, msg = ver.verify(ver.verification_code)
        assert success is True


class TestDownloadRequestModel:

    def test_create(self, db):
        dr = DownloadRequest(
            first_name='John', last_name='Doe',
            email='john@example.com', institution='Uni',
            country='US', reason='Research',
            format='csv', status='pending'
        )
        db.session.add(dr)
        db.session.commit()
        assert dr.id is not None
        assert dr.status == 'pending'

    def test_repr(self, db):
        dr = DownloadRequest(first_name='John', last_name='Doe', email='j@e.com',
                            institution='U', country='US', reason='R', format='csv')
        db.session.add(dr)
        db.session.commit()
        assert 'DownloadRequest' in repr(dr)
        assert str(dr.id) in repr(dr)


class TestDownloadRequestItemModel:

    def test_create(self, db):
        dr = DownloadRequest(
            first_name='J', last_name='D', email='j@e.com',
            institution='U', country='US', reason='R', format='csv'
        )
        db.session.add(dr)
        db.session.flush()

        item = DownloadRequestItem(request_id=dr.id, is_element_id=1)
        db.session.add(item)
        db.session.commit()
        assert item.id is not None


class TestSystemConfigAdvanced:

    def test_number_type(self, db):
        config = SystemConfig(
            config_key='num_key', config_value='42',
            config_type='number'
        )
        db.session.add(config)
        db.session.commit()

        val = SystemConfig.get_value('num_key')
        assert val == 42
        assert isinstance(val, int)

    def test_float_number(self, db):
        config = SystemConfig(
            config_key='float_key', config_value='3.14',
            config_type='number'
        )
        db.session.add(config)
        db.session.commit()

        val = SystemConfig.get_value('float_key')
        assert val == 3.14

    def test_json_type(self, db):
        import json
        config = SystemConfig(
            config_key='json_key',
            config_value=json.dumps({'a': 1, 'b': 2}),
            config_type='json'
        )
        db.session.add(config)
        db.session.commit()

        val = SystemConfig.get_value('json_key')
        assert val == {'a': 1, 'b': 2}

    def test_invalid_number_returns_default(self, db):
        config = SystemConfig(
            config_key='bad_num', config_value='not-a-number',
            config_type='number'
        )
        db.session.add(config)
        db.session.commit()

        val = SystemConfig.get_value('bad_num', default=0)
        assert val == 0


class TestUserModelEdgeCases:

    def test_user_without_names(self, db):
        user = User(username='noname', role='visitor')
        assert user.full_name == ''

    def test_user_first_name_only(self, db):
        user = User(username='firstonly', first_name='Alice', role='visitor')
        assert user.full_name == 'Alice'

    def test_user_with_all_fields(self, db):
        user = User(
            username='fulluser', email='full@example.com',
            role='admin', first_name='John', last_name='Doe',
            institution='MIT', department='Biology',
            country='US', is_active=True
        )
        user.password = 'StrongPass123'
        db.session.add(user)
        db.session.commit()

        d = user.to_dict()
        assert d['username'] == 'fulluser'
        assert d['institution'] == 'MIT'
        assert d['country'] == 'US'

    def test_created_at_auto_set(self, db):
        user = User(username='timeduser', role='visitor')
        user.password = 'SomePass123'
        db.session.add(user)
        db.session.commit()
        assert user.created_at is not None


class TestISElementToDict:

    def test_to_dict_with_sequences(self, db, sample_elements):
        el = sample_elements[0]
        d = el.to_dict(include_sequences=True)
        assert 'is_sequence' in d
        assert 'left_flank' in d
        assert 'right_flank' in d

    def test_to_dict_without_sequences(self, db, sample_elements):
        el = sample_elements[0]
        d = el.to_dict()
        assert 'is_sequence' not in d

    def test_flank_properties(self, db):
        seq = 'A' * 100
        el = ISElement(name='FlankTest', family='IS1', is_sequence=seq)
        db.session.add(el)
        db.session.commit()

        assert el.left_flank == seq[:50]
        assert el.right_flank == seq[-50:]

    def test_flank_none_when_no_sequence(self, db):
        el = ISElement(name='NoSeq', family='IS1')
        db.session.add(el)
        db.session.commit()

        assert el.left_flank is None
        assert el.right_flank is None
