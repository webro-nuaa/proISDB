# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import current_user
from app import db, cache
from app.models import ISElement, KnowledgeArticle, PageView, SearchLog, User
from app.forms.search import SearchForm

main = Blueprint('main', __name__)


@main.route('/health')
def health():
    status = {'app': 'ok', 'version': current_app.config.get('VERSION', 'unknown'), 'database': 'ok', 'redis': 'ok'}

    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception as e:
        status['database'] = f'error: {str(e)[:100]}'

    try:
        cache.set('health:check', 'ok', timeout=10)
        if cache.get('health:check') != 'ok':
            status['redis'] = 'error: read/write mismatch'
    except Exception as e:
        status['redis'] = f'error: {str(e)[:100]}'

    is_healthy = all(v == 'ok' for v in status.values())
    code = 200 if is_healthy else 503
    return jsonify(status), code


@main.route('/')
def index():
    PageView.log_view(
        page_type='home',
        user=current_user if current_user.is_authenticated else None,
        request=request
    )

    total_elements = cache.get('stats:total_elements')
    if total_elements is None:
        total_elements = ISElement.query.filter_by(status='approved').count()
        cache.set('stats:total_elements', total_elements, timeout=300)

    total_articles = cache.get('stats:total_articles')
    if total_articles is None:
        total_articles = KnowledgeArticle.query.filter_by(status='published').count()
        cache.set('stats:total_articles', total_articles, timeout=300)

    recent_elements = cache.get('stats:recent_elements')
    if recent_elements is None:
        recent_elements = ISElement.query.filter_by(status='approved')\
                                       .order_by(ISElement.created_at.desc())\
                                       .limit(5).all()
        cache.set('stats:recent_elements', recent_elements, timeout=120)

    featured_articles = KnowledgeArticle.get_featured(limit=3)

    family_stats = cache.get('stats:family_stats')
    if family_stats is None:
        from sqlalchemy import func
        try:
            family_stats = db.session.query(
                ISElement.family,
                func.count(ISElement.id).label('count')
            ).filter_by(status='approved')\
             .group_by(ISElement.family)\
             .order_by(func.count(ISElement.id).desc())\
             .limit(10).all()
            cache.set('stats:family_stats', family_stats, timeout=600)
        except Exception:
            family_stats = []

    search_form = SearchForm()

    return render_template('main/index.html',
                         total_elements=total_elements,
                         total_articles=total_articles,
                         recent_elements=recent_elements,
                         featured_articles=featured_articles,
                         family_stats=family_stats,
                         search_form=search_form)


@main.route('/about')
def about():
    PageView.log_view(
        page_type='other',
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    return render_template('main/about.html')
