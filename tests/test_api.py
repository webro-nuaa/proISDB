# -*- coding: utf-8 -*-
"""Tests for API features."""
import pytest


class TestAPIIndex:

    def test_api_index(self, client):
        rv = client.get('/api/')
        assert rv.status_code == 200

    def test_api_families(self, client, sample_elements):
        rv = client.get('/api/families')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True
        assert isinstance(data['families'], list)


class TestMarkdownPreview:

    def test_preview_no_login(self, client):
        rv = client.post('/api/preview-markdown')
        assert rv.status_code == 302

    def test_preview_empty_content(self, admin_client):
        rv = admin_client.post('/api/preview-markdown', data={'content': ''})
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True

    def test_preview_with_content(self, admin_client):
        rv = admin_client.post('/api/preview-markdown', data={
            'content': '# Hello\n\nThis is **bold** text.'
        })
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True
        assert 'html' in data


class TestSearchExport:

    def test_export_json(self, client, sample_elements):
        rv = client.get('/search/export?query=IS1')
        assert rv.status_code == 200
        data = rv.get_json()
        assert 'count' in data
        assert 'data' in data

    def test_export_with_family(self, client, sample_elements):
        rv = client.get('/search/export?family=IS3')
        assert rv.status_code == 200
        data = rv.get_json()
        assert 'count' in data
