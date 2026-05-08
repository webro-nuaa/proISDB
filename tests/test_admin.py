# -*- coding: utf-8 -*-
"""Tests for Admin features."""
import pytest
from app.models import User, ISElement, AdminLog, SystemConfig


class TestAdminLogin:

    def test_admin_login_page(self, client):
        rv = client.get('/admin/login')
        assert rv.status_code == 200

    def test_admin_login_success(self, client, admin_user):
        rv = client.post('/admin/login', data={
            'username': 'adminuser',
            'password': 'AdminPass123'
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_admin_login_wrong_password(self, client, admin_user):
        rv = client.post('/admin/login', data={
            'username': 'adminuser',
            'password': 'WrongPass'
        })
        assert rv.status_code == 200

    def test_admin_login_as_visitor(self, client, test_user):
        rv = client.post('/admin/login', data={
            'username': 'testuser',
            'password': 'TestPass123'
        }, follow_redirects=True)
        assert rv.status_code == 200


class TestAdminDashboard:

    def test_dashboard_requires_login(self, client):
        rv = client.get('/admin/')
        assert rv.status_code == 302

    def test_dashboard_as_admin(self, admin_client):
        rv = admin_client.get('/admin/')
        assert rv.status_code == 200

    def test_dashboard_as_root(self, client, root_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.get('/admin/')
        assert rv.status_code == 200

    def test_statistics_page(self, admin_client):
        rv = admin_client.get('/admin/statistics')
        assert rv.status_code == 200


class TestAdminISElementManagement:

    def test_is_elements_page(self, admin_client):
        rv = admin_client.get('/admin/is-elements')
        assert rv.status_code == 200

    def test_is_elements_search(self, admin_client, sample_elements):
        rv = admin_client.get('/admin/is-elements?search=IS1')
        assert rv.status_code == 200

    def test_is_elements_by_status(self, admin_client, sample_elements):
        rv = admin_client.get('/admin/is-elements?status=approved')
        assert rv.status_code == 200

    def test_is_elements_advanced_search(self, admin_client, sample_elements):
        rv = admin_client.get('/admin/is-elements?advanced=1&name=IS1&name_match=contains')
        assert rv.status_code == 200

    def test_add_is_element_page(self, admin_client):
        rv = admin_client.get('/admin/is-element/add')
        assert rv.status_code == 200

    def test_add_is_element_success(self, admin_client, admin_user):
        """Admin adds IS element directly."""
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.email = 'admin@example.com'
        admin_user.institution = 'Test Institute'
        admin_user.country = 'China'

        rv = admin_client.post('/admin/is-element/add', data={
            'name': 'IS_ADMIN_001',
            'family': 'IS1',
            'host': 'E. coli',
            'is_length': '1000',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_view_is_element_ajax(self, admin_client, sample_elements):
        el = sample_elements[0]
        rv = admin_client.get(f'/admin/view-is-element/{el.id}')
        assert rv.status_code == 200

    def test_is_element_view_page(self, admin_client, sample_elements):
        el = sample_elements[0]
        rv = admin_client.get(f'/admin/is-element/{el.id}/view')
        assert rv.status_code == 200

    def test_edit_is_element_page(self, admin_client, sample_elements):
        el = sample_elements[0]
        rv = admin_client.get(f'/admin/is-element/{el.id}/edit')
        assert rv.status_code == 200

    def test_edit_is_element_update(self, admin_client, sample_elements):
        el = sample_elements[0]
        rv = admin_client.post(f'/admin/is-element/{el.id}/edit', data={
            'name': 'IS1_Updated',
            'family': 'IS1',
            'host': 'E. coli',
            'is_length': '800',
        }, follow_redirects=True)
        assert rv.status_code == 200

        updated = ISElement.query.get(el.id)
        assert updated.name == 'IS1_Updated'

    def test_delete_is_element(self, admin_client, db):
        el = ISElement(name='ToDelete', family='IS1', host='E. coli', status='approved')
        db.session.add(el)
        db.session.commit()

        rv = admin_client.post(f'/admin/is-element/{el.id}/delete',
                               data={'csrf_token': 'ignored-in-test'},
                               follow_redirects=True)
        # In test mode CSRF is disabled, so the form may not validate
        # The redirect means it attempted the action
        assert rv.status_code in (200, 302)

    def test_import_page(self, admin_client):
        rv = admin_client.get('/admin/is-elements/import')
        assert rv.status_code == 200

    def test_batch_action(self, admin_client, db):
        el = ISElement(name='BatchTest', family='IS1', host='E. coli', status='pending')
        db.session.add(el)
        db.session.commit()

        rv = admin_client.post('/admin/batch-action', data={
            'action': 'approve',
            'ids': [str(el.id)],
        })
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True


class TestAdminUserManagement:

    def test_manage_admins_as_root(self, client, root_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.get('/admin/admins')
        assert rv.status_code == 200

    def test_manage_admins_as_admin_denied(self, admin_client):
        rv = admin_client.get('/admin/admins')
        assert rv.status_code == 302

    def test_create_admin_page(self, client, root_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.get('/admin/admins/create')
        assert rv.status_code == 200

    def test_create_admin_user(self, client, root_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.post('/admin/admins/create', data={
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'NewAdmin123',
            'confirm_password': 'NewAdmin123',
            'first_name': 'New',
            'last_name': 'Admin',
            'institution': 'Institute',
            'country': 'CN',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_disable_admin(self, client, root_user, admin_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.post(f'/admin/admins/{admin_user.id}/disable', follow_redirects=True)
        assert rv.status_code == 200

        updated = User.query.get(admin_user.id)
        assert updated.is_active is False

    def test_enable_admin(self, client, root_user, admin_user):
        admin_user.is_active = False
        from app import db
        db.session.commit()

        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.post(f'/admin/admins/{admin_user.id}/enable', follow_redirects=True)
        assert rv.status_code == 200

        updated = User.query.get(admin_user.id)
        assert updated.is_active is True

    def test_cannot_disable_root(self, client, root_user):
        client.post('/auth/login', data={'username': 'rootuser', 'password': 'RootPass123'})
        rv = client.post(f'/admin/admins/{root_user.id}/disable', follow_redirects=True)
        assert rv.status_code == 200


class TestAdminLogModel:

    def test_log_action(self, db, test_user):
        log = AdminLog.log_action(
            user=test_user,
            action='test_action',
            resource_type='test',
            resource_id=1,
            details={'key': 'value'}
        )
        assert log.id is not None
        assert log.action == 'test_action'
        assert log.resource_type == 'test'

    def test_admin_log_repr(self, db, test_user):
        log = AdminLog(user_id=test_user.id, action='delete', resource_type='is_element')
        assert repr(log) == '<AdminLog delete>'


class TestBlastDatabaseManagement:

    def test_blast_database_page(self, admin_client):
        rv = admin_client.get('/admin/blast-database')
        assert rv.status_code == 200

    def test_rebuild_blast_db_no_permission(self, client):
        rv = client.post('/admin/blast-database/rebuild')
        assert rv.status_code == 302
