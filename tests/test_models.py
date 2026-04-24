# -*- coding: utf-8 -*-
import pytest
from app.models import User, ISElement, SystemConfig, SearchLog


class TestUserModel:

    def test_create_user(self, db):
        user = User(
            username='newuser',
            email='new@example.com',
            role='visitor',
            first_name='New',
            last_name='User',
            is_active=True
        )
        user.password = 'Password123'
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.role == 'visitor'
        assert user.is_active is True

    def test_password_hashing(self, db):
        user = User(username='hashtest', email='hash@example.com', role='visitor')
        user.password = 'MySecret123'

        assert user.password_hash is not None
        assert user.password_hash != 'MySecret123'
        assert user.verify_password('MySecret123') is True
        assert user.verify_password('WrongPassword') is False

    def test_password_not_readable(self, db):
        user = User(username='readtest', email='read@example.com', role='visitor')
        user.password = 'Secret123'

        with pytest.raises(AttributeError):
            _ = user.password

    def test_full_name(self, db):
        user = User(username='nametest', first_name='John', last_name='Doe', role='visitor')
        assert user.full_name == 'John Doe'

        user2 = User(username='nametest2', first_name='Jane', role='visitor')
        assert user2.full_name == 'Jane'

        user3 = User(username='nametest3', role='visitor')
        assert user3.full_name == ''

    def test_role_permissions(self, db):
        root = User(username='root1', role='root')
        admin = User(username='admin1', role='admin')
        visitor = User(username='visitor1', role='visitor')

        assert root.is_root() is True
        assert root.is_admin() is False
        assert root.has_admin_permission() is True

        assert admin.is_root() is False
        assert admin.is_admin() is True
        assert admin.has_admin_permission() is True

        assert visitor.is_root() is False
        assert visitor.is_admin() is False
        assert visitor.has_admin_permission() is False

    def test_to_dict(self, db):
        user = User(
            username='dicttest',
            email='dict@example.com',
            role='visitor',
            first_name='Test',
            is_active=True
        )
        user.password = 'Pass123'
        db.session.add(user)
        db.session.commit()

        d = user.to_dict()
        assert d['username'] == 'dicttest'
        assert d['email'] == 'dict@example.com'
        assert d['role'] == 'visitor'
        assert 'password_hash' not in d
        assert d['is_active'] is True

    def test_user_repr(self, db):
        user = User(username='reprtest', role='visitor')
        assert repr(user) == '<User reprtest>'


class TestISElementModel:

    def test_create_element(self, db):
        el = ISElement(
            name='IS100',
            family='IS1',
            group='IS1',
            host='E. coli',
            status='approved',
            is_length=768
        )
        db.session.add(el)
        db.session.commit()

        assert el.id is not None
        assert el.name == 'IS100'
        assert el.status == 'approved'

    def test_default_status_is_pending(self, db):
        el = ISElement(name='IS200', family='IS3')
        db.session.add(el)
        db.session.commit()

        assert el.status == 'pending'

    def test_search_approved_only(self, db, sample_elements):
        results = ISElement.search('', status='approved', page=1, per_page=20)
        names = [e.name for e in results.items]
        assert 'IS5-pending' not in names
        assert 'IS1' in names

    def test_search_by_text(self, db, sample_elements):
        results = ISElement.search('IS1', status='approved', page=1, per_page=20)
        assert results.total >= 1
        for item in results.items:
            assert 'IS1' in item.name or 'IS1' in item.family

    def test_search_by_family(self, db, sample_elements):
        results = ISElement.search('', family='IS3', status='approved', page=1, per_page=20)
        assert results.total >= 2
        for item in results.items:
            assert item.family == 'IS3'

    def test_search_by_host(self, db, sample_elements):
        results = ISElement.search('', host='Escherichia', status='approved', page=1, per_page=20)
        assert results.total >= 2
        for item in results.items:
            assert 'Escherichia' in (item.host or '')

    def test_get_families(self, db, sample_elements):
        families = ISElement.get_families()
        family_names = [f[0] for f in families]
        assert 'IS1' in family_names
        assert 'IS3' in family_names
        assert 'IS5' in family_names

    def test_get_hosts(self, db, sample_elements):
        hosts = ISElement.get_hosts()
        host_names = [h[0] for h in hosts]
        assert 'Escherichia coli' in host_names

    def test_to_dict(self, db, sample_elements):
        el = sample_elements[0]
        d = el.to_dict()
        assert d['name'] == 'IS1'
        assert d['family'] == 'IS1'
        assert 'password' not in d

    def test_element_repr(self, db):
        el = ISElement(name='ISrepr')
        assert repr(el) == '<ISElement ISrepr>'


class TestSystemConfigModel:

    def test_get_value(self, db, system_configs):
        val = SystemConfig.get_value('site_name')
        assert val == 'proISDB'

    def test_get_value_boolean(self, db, system_configs):
        val = SystemConfig.get_value('enable_registration')
        assert val is True

    def test_get_value_default(self, db):
        val = SystemConfig.get_value('nonexistent_key', default='fallback')
        assert val == 'fallback'

    def test_set_value_new(self, db):
        config = SystemConfig.set_value('new_key', 'new_value', description='Test')
        assert config.config_value == 'new_value'
        assert SystemConfig.get_value('new_key') == 'new_value'

    def test_set_value_update(self, db, system_configs):
        SystemConfig.set_value('site_name', 'UpdatedName')
        assert SystemConfig.get_value('site_name') == 'UpdatedName'


class TestSearchLogModel:

    def test_log_search(self, db):
        log = SearchLog.log_search(
            search_term='IS1',
            search_type='is_elements_simple',
            results_count=5
        )
        assert log.id is not None
        assert log.search_term == 'IS1'
        assert log.results_count == 5
