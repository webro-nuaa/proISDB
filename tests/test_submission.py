# -*- coding: utf-8 -*-
"""Tests for Submission features."""
import pytest
from app.models import ISElement, SubmissionHistory


class TestSubmissionViews:

    def test_submission_index_redirect(self, client):
        rv = client.get('/submission/')
        assert rv.status_code == 302

    def test_submit_page(self, client):
        rv = client.get('/submission/submit')
        assert rv.status_code == 200

    def test_submit_element_success(self, client, db):
        rv = client.post('/submission/submit', data={
            'name': 'IS_Test_001',
            'family': 'IS3',
            'host': 'E. coli',
            'first_name': 'John',
            'last_name': 'Doe',
            'institution': 'Test University',
            'country': 'USA',
            'email': 'john@example.com',
            'is_length': '1200',
            'orf_number': '2',
            'is_sequence': 'ATCGATCG',
        }, follow_redirects=True)
        assert rv.status_code == 200

        element = ISElement.query.filter_by(name='IS_Test_001').first()
        assert element is not None
        assert element.status == 'pending'

    def test_submit_duplicate_name(self, client, db, sample_elements):
        rv = client.post('/submission/submit', data={
            'name': 'IS1',
            'family': 'IS1',
            'host': 'E. coli',
            'first_name': 'Test',
            'last_name': 'User',
            'institution': 'Uni',
            'country': 'US',
            'email': 'test@example.com',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_pending_review_requires_login(self, client):
        rv = client.get('/submission/pending-review')
        assert rv.status_code == 302

    def test_pending_review_as_admin(self, admin_client, db):
        element = ISElement(name='Pending1', family='IS1', host='E. coli', status='pending')
        db.session.add(element)
        db.session.commit()

        rv = admin_client.get('/submission/pending-review')
        assert rv.status_code == 200

    def test_review_page(self, admin_client, db):
        element = ISElement(name='ReviewMe', family='IS3', host='E. coli', status='pending')
        db.session.add(element)
        db.session.commit()

        rv = admin_client.get(f'/submission/review/{element.id}')
        assert rv.status_code == 200

    def test_approve_submission(self, admin_client, db):
        element = ISElement(name='ApproveMe', family='IS1', host='E. coli', status='pending')
        db.session.add(element)
        db.session.commit()

        rv = admin_client.post(f'/submission/review/{element.id}', data={
            'status': 'approved',
            'review_notes': 'Looks good',
        }, follow_redirects=True)
        assert rv.status_code == 200

        updated = ISElement.query.get(element.id)
        assert updated.status == 'approved'

    def test_reject_submission(self, admin_client, db):
        element = ISElement(name='RejectMe', family='IS5', host='B. subtilis', status='pending')
        db.session.add(element)
        db.session.commit()

        rv = admin_client.post(f'/submission/review/{element.id}', data={
            'status': 'rejected',
            'review_notes': 'Not valid',
        }, follow_redirects=True)
        assert rv.status_code == 200

        updated = ISElement.query.get(element.id)
        assert updated.status == 'rejected'

    def test_review_not_found(self, admin_client):
        rv = admin_client.get('/submission/review/99999')
        assert rv.status_code == 404

    def test_review_requires_admin(self, client, logged_in_client, db):
        element = ISElement(name='NoPerm', family='IS1', host='E. coli', status='pending')
        db.session.add(element)
        db.session.commit()

        rv = logged_in_client.get(f'/submission/review/{element.id}')
        assert rv.status_code == 302


class TestValidateNameAPI:

    def test_validate_new_name(self, client, db):
        rv = client.get('/submission/api/validate-name?name=BrandNewIS')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['exists'] is False

    def test_validate_existing_name(self, client, db, sample_elements):
        rv = client.get('/submission/api/validate-name?name=IS1')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['exists'] is True

    def test_validate_empty_name(self, client):
        rv = client.get('/submission/api/validate-name?name=')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['exists'] is False


class TestSubmissionHistoryModel:

    def test_create_history(self, db):
        element = ISElement(name='HistoryTest', family='IS1', host='E. coli')
        db.session.add(element)
        db.session.flush()

        history = SubmissionHistory(
            is_element_id=element.id,
            action='create',
            new_data={'name': 'HistoryTest', 'family': 'IS1'},
            status='pending'
        )
        db.session.add(history)
        db.session.commit()

        assert history.id is not None
        assert history.action == 'create'

    def test_history_repr(self, db):
        h = SubmissionHistory(is_element_id=1, action='create')
        assert repr(h) == '<SubmissionHistory None>'
