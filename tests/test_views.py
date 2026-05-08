# -*- coding: utf-8 -*-
import pytest
from app.models import User, ISElement


class TestMainViews:

    def test_health_endpoint(self, client):
        rv = client.get('/health')
        data = rv.get_json()
        assert data['app'] == 'ok'
        assert data['database'] == 'ok'
        # Redis may be unavailable in test environment (503 if cache fails)
        assert 'redis' in data

    def test_home_page(self, client):
        rv = client.get('/')
        assert rv.status_code == 200

    def test_about_page(self, client):
        rv = client.get('/about')
        assert rv.status_code == 200


class TestAuthViews:

    def test_login_page_get(self, client):
        rv = client.get('/auth/login')
        assert rv.status_code == 200

    def test_login_success(self, client, test_user):
        rv = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123'
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_login_wrong_password(self, client, test_user):
        rv = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        assert rv.status_code == 200
        assert b'Incorrect' in rv.data or b'incorrect' in rv.data.lower()

    def test_login_nonexistent_user(self, client):
        rv = client.post('/auth/login', data={
            'username': 'nouser',
            'password': 'NoPass123'
        })
        assert rv.status_code == 200
        assert b'Incorrect' in rv.data or b'incorrect' in rv.data.lower()

    def test_logout_requires_login(self, client):
        rv = client.get('/auth/logout')
        assert rv.status_code == 302

    def test_logout_success(self, logged_in_client):
        rv = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert rv.status_code == 200

    def test_profile_requires_login(self, client):
        rv = client.get('/auth/profile')
        assert rv.status_code == 302

    def test_profile_logged_in(self, logged_in_client):
        rv = logged_in_client.get('/auth/profile')
        assert rv.status_code == 200

    def test_change_password_page(self, logged_in_client):
        rv = logged_in_client.get('/auth/change-password')
        assert rv.status_code == 200


class TestSearchViews:

    def test_search_page_get(self, client):
        rv = client.get('/search/')
        assert rv.status_code == 200

    def test_search_with_query(self, client, sample_elements):
        rv = client.get('/search/?query=IS1')
        assert rv.status_code == 200

    def test_search_empty_query(self, client, sample_elements):
        rv = client.get('/search/?query=')
        assert rv.status_code == 200

    def test_search_short_query(self, client, sample_elements):
        rv = client.get('/search/?query=IS')
        assert rv.status_code == 200

    def test_advanced_search_page(self, client, sample_elements):
        rv = client.get('/search/?advanced=1&name=IS1')
        assert rv.status_code == 200

    def test_advanced_search_by_family(self, client, sample_elements):
        rv = client.get('/search/?advanced=1&family=IS3')
        assert rv.status_code == 200

    def test_advanced_search_by_host(self, client, sample_elements):
        rv = client.get('/search/?advanced=1&host=Escherichia')
        assert rv.status_code == 200

    def test_element_detail(self, client, sample_elements):
        el = sample_elements[0]
        rv = client.get(f'/search/element/{el.id}')
        assert rv.status_code == 200

    def test_element_detail_not_found(self, client, db):
        rv = client.get('/search/element/99999')
        assert rv.status_code == 404

    def test_api_suggestions(self, client, sample_elements):
        rv = client.get('/search/api/suggestions?q=IS')
        assert rv.status_code == 200
        data = rv.get_json()
        assert isinstance(data, list)

    def test_api_suggestions_too_short(self, client, sample_elements):
        rv = client.get('/search/api/suggestions?q=I')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data == []

    def test_api_families(self, client, sample_elements):
        rv = client.get('/search/api/families')
        assert rv.status_code == 200
        data = rv.get_json()
        assert isinstance(data, list)
        assert 'IS1' in data
        assert 'IS3' in data

    def test_export_results(self, client, sample_elements):
        rv = client.get('/search/export?query=IS1')
        assert rv.status_code == 200
        data = rv.get_json()
        assert 'count' in data
        assert 'data' in data


class TestErrorPages:

    def test_404_page(self, client):
        rv = client.get('/nonexistent-page')
        assert rv.status_code == 404
