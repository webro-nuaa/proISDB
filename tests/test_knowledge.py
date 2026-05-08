# -*- coding: utf-8 -*-
"""Tests for Knowledge base features."""
import pytest
from app.models import KnowledgeArticle, KnowledgeCategory, KnowledgeTag


class TestKnowledgeCategoryModel:

    def test_create_category(self, db):
        cat = KnowledgeCategory(name='Test Category', description='A test description')
        db.session.add(cat)
        db.session.commit()

        assert cat.id is not None
        assert cat.name == 'Test Category'
        assert cat.is_active is True

    def test_to_dict(self, db):
        cat = KnowledgeCategory(name='Dict Cat', description='test', sort_order=5)
        db.session.add(cat)
        db.session.commit()

        d = cat.to_dict()
        assert d['name'] == 'Dict Cat'
        assert d['sort_order'] == 5

    def test_parent_child(self, db):
        parent = KnowledgeCategory(name='Parent')
        db.session.add(parent)
        db.session.flush()
        child = KnowledgeCategory(name='Child', parent_id=parent.id)
        db.session.add(child)
        db.session.commit()

        assert child.parent == parent
        assert child in parent.children

    def test_repr(self, db):
        cat = KnowledgeCategory(name='Repr Cat')
        assert repr(cat) == '<KnowledgeCategory Repr Cat>'


class TestKnowledgeTagModel:

    def test_create_tag(self, db):
        tag = KnowledgeTag(name='test-tag', color='#ff0000')
        db.session.add(tag)
        db.session.commit()

        assert tag.id is not None
        assert tag.name == 'test-tag'
        assert tag.color == '#ff0000'

    def test_repr(self, db):
        tag = KnowledgeTag(name='reprtag')
        assert repr(tag) == '<KnowledgeTag reprtag>'


class TestKnowledgeArticleModel:

    @pytest.fixture
    def article(self, db, test_user):
        article = KnowledgeArticle(
            title='Test Article', slug='test-article',
            content='# Hello\n\nThis is a test article.',
            summary='A test summary',
            author_id=test_user.id,
            status='published'
        )
        db.session.add(article)
        db.session.commit()
        return article

    def test_create_article(self, db, test_user):
        article = KnowledgeArticle(
            title='New Article', slug='new-article',
            content='Content here.', author_id=test_user.id, status='draft'
        )
        db.session.add(article)
        db.session.commit()
        assert article.id is not None
        assert article.status == 'draft'

    def test_get_featured(self, db, test_user):
        featured = KnowledgeArticle(
            title='Featured Post', slug='featured-post',
            content='Content', author_id=test_user.id,
            status='published', is_featured=True
        )
        db.session.add(featured)
        db.session.commit()

        articles = KnowledgeArticle.get_featured()
        assert len(articles) >= 1
        assert articles[0].is_featured is True

    def test_get_recent(self, db, test_user):
        for i in range(15):
            a = KnowledgeArticle(
                title=f'Article {i}', slug=f'article-{i}',
                content='Content', author_id=test_user.id,
                status='published'
            )
            db.session.add(a)
        db.session.commit()

        recent = KnowledgeArticle.get_recent(limit=5)
        assert len(recent) <= 5

    def test_increment_view_count(self, db, article):
        old_count = article.view_count
        article.increment_view_count()
        assert article.view_count == old_count + 1

    def test_to_dict(self, db, article):
        tag = KnowledgeTag(name='python')
        db.session.add(tag)
        db.session.flush()
        article.tags.append(tag)
        db.session.commit()

        d = article.to_dict()
        assert d['title'] == 'Test Article'
        assert d['slug'] == 'test-article'
        assert 'python' in d['tags']
        assert 'content' not in d

    def test_to_dict_include_content(self, db, article):
        d = article.to_dict(include_content=True)
        assert 'content' in d

    def test_search(self, db, test_user):
        for i, term in enumerate(['python', 'javascript', 'python web']):
            a = KnowledgeArticle(
                title=f'{term} guide', slug=f'{term}-guide-{i}',
                content=f'Content about {term}', author_id=test_user.id,
                status='published'
            )
            db.session.add(a)
        db.session.commit()

        results = KnowledgeArticle.search('python', page=1, per_page=10)
        assert results.total >= 2

    def test_repr(self, db):
        a = KnowledgeArticle(title='Repr Title', slug='repr-title', content='x', author_id=1)
        assert repr(a) == '<KnowledgeArticle Repr Title>'


class TestKnowledgeViews:

    def test_knowledge_index(self, client):
        rv = client.get('/knowledge/')
        assert rv.status_code == 200

    def test_tag_articles(self, client, db):
        tag = KnowledgeTag(name='genetics')
        db.session.add(tag)
        db.session.commit()

        rv = client.get(f'/knowledge/tag/{tag.name}')
        assert rv.status_code == 200

    def test_article_detail(self, client, db, test_user):
        article = KnowledgeArticle(
            title='Detail Article', slug='detail-article',
            content='# Content', author_id=test_user.id, status='published'
        )
        db.session.add(article)
        db.session.commit()

        rv = client.get(f'/knowledge/article/{article.slug}')
        assert rv.status_code == 200

    def test_article_detail_not_found(self, client):
        rv = client.get('/knowledge/article/nonexistent')
        assert rv.status_code == 404

    def test_tag_articles_not_found(self, client):
        rv = client.get('/knowledge/tag/nonexistent-tag')
        assert rv.status_code == 404


class TestKnowledgeAdminViews:

    def test_admin_index_requires_login(self, client):
        rv = client.get('/knowledge/admin')
        assert rv.status_code == 302

    def test_admin_index_as_admin(self, admin_client):
        rv = admin_client.get('/knowledge/admin')
        assert rv.status_code == 200

    def test_admin_articles(self, admin_client):
        rv = admin_client.get('/knowledge/admin/articles')
        assert rv.status_code == 200

    def test_admin_new_article_page(self, admin_client):
        rv = admin_client.get('/knowledge/admin/article/new')
        assert rv.status_code == 200

    def test_create_article(self, admin_client):
        rv = admin_client.post('/knowledge/admin/article/new', data={
            'title': 'Brand New Article',
            'content': '# Hello World',
            'summary': 'A summary',
            'status': 'published',
            'tags': 'science,biology',
            'is_featured': 'y',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_admin_view_article(self, admin_client, db, test_user):
        article = KnowledgeArticle(
            title='View Article', slug='view-article',
            content='Content', author_id=test_user.id, status='published'
        )
        db.session.add(article)
        db.session.commit()

        rv = admin_client.get(f'/knowledge/admin/article/{article.id}/view')
        assert rv.status_code == 200

    def test_admin_edit_article_page(self, admin_client, db, test_user):
        article = KnowledgeArticle(
            title='Edit Me', slug='edit-me',
            content='Old content', author_id=test_user.id, status='draft'
        )
        db.session.add(article)
        db.session.commit()

        rv = admin_client.get(f'/knowledge/admin/article/{article.id}/edit')
        assert rv.status_code == 200

    def test_update_article(self, admin_client, db, test_user):
        article = KnowledgeArticle(
            title='Old Title', slug='old-title',
            content='Old content', author_id=test_user.id, status='draft'
        )
        db.session.add(article)
        db.session.commit()

        rv = admin_client.post(f'/knowledge/admin/article/{article.id}/edit', data={
            'title': 'Updated Title',
            'content': 'New content',
            'summary': 'Updated summary',
            'status': 'published',
            'tags': 'updated',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_toggle_publish(self, admin_client, db, test_user):
        article = KnowledgeArticle(
            title='Toggle Me', slug='toggle-me',
            content='Content', author_id=test_user.id, status='draft'
        )
        db.session.add(article)
        db.session.commit()

        rv = admin_client.post(
            f'/knowledge/admin/article/{article.id}/toggle-publish',
            json={'status': 'published'}
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True

    def test_delete_article(self, admin_client, db, test_user):
        article = KnowledgeArticle(
            title='Delete Me', slug='delete-me',
            content='Content', author_id=test_user.id, status='draft'
        )
        db.session.add(article)
        db.session.commit()

        rv = admin_client.post(f'/knowledge/admin/article/{article.id}/delete', follow_redirects=True)
        assert rv.status_code == 200

    def test_upload_image_no_permission(self, client):
        rv = client.post('/knowledge/admin/upload-image')
        assert rv.status_code == 302

    def test_upload_image_no_file(self, admin_client):
        rv = admin_client.post('/knowledge/admin/upload-image')
        assert rv.status_code == 400
        data = rv.get_json()
        assert data['success'] is False
