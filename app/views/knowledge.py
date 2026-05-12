# -*- coding: utf-8 -*-
"""
科普知识视图
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import KnowledgeArticle, KnowledgeCategory, KnowledgeTag, PageView, AdminLog
from app.forms.knowledge import ArticleForm, CategoryForm, TagForm
from app.utils.helpers import slugify

knowledge = Blueprint('knowledge', __name__)

@knowledge.route('/')
def index():
    """Knowledge index page"""
    PageView.log_view(
        page_type='other',
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    # 科普文章使用较小的分页数量，方便阅读
    per_page = current_app.config.get('SEARCH_RESULTS_PER_PAGE', 8)
    
    # 获取所有已发布的文章
    articles = KnowledgeArticle.query.filter_by(status='published')\
                                    .order_by(KnowledgeArticle.published_at.desc())\
                                    .paginate(
                                        page=page,
                                        per_page=per_page,
                                        error_out=False
                                    )
    
    return render_template('knowledge/index.html',
                         articles=articles)

@knowledge.route('/article/<slug>')
def article_detail(slug):
    """Article detail page"""
    article = KnowledgeArticle.query.filter_by(slug=slug, status='published').first_or_404()
    
    # 记录页面访问
    PageView.log_view(
        page_type='knowledge_article',
        page_id=article.id,
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    
    # 增加浏览次数
    article.increment_view_count()
    
    # 获取相关文章（基于共同标签或最新文章）
    related_articles = []
    if article.tags:
        # 基于标签的相关文章
        tag_ids = [tag.id for tag in article.tags]
        related_articles = db.session.query(KnowledgeArticle)\
                                    .join(KnowledgeArticle.tags)\
                                    .filter(KnowledgeTag.id.in_(tag_ids),
                                           KnowledgeArticle.id != article.id,
                                           KnowledgeArticle.status == 'published')\
                                    .group_by(KnowledgeArticle.id)\
                                    .order_by(db.func.count(KnowledgeTag.id).desc())\
                                    .limit(4).all()
    
    # 如果基于标签的相关文章不足，用最新文章补充
    if len(related_articles) < 4:
        latest_articles = KnowledgeArticle.query\
                                         .filter(KnowledgeArticle.id != article.id,
                                                KnowledgeArticle.status == 'published')\
                                         .order_by(KnowledgeArticle.published_at.desc())\
                                         .limit(4 - len(related_articles)).all()
        related_articles.extend(latest_articles)
    
    # 获取热门文章
    popular_articles = KnowledgeArticle.query\
                                      .filter(KnowledgeArticle.id != article.id,
                                             KnowledgeArticle.status == 'published')\
                                      .order_by(KnowledgeArticle.view_count.desc())\
                                      .limit(5).all()
    
    # 获取热门标签
    popular_tags = db.session.query(KnowledgeTag)\
                            .join(KnowledgeArticle.tags)\
                            .filter(KnowledgeArticle.status == 'published')\
                            .group_by(KnowledgeTag.id)\
                            .order_by(db.func.count(KnowledgeArticle.id).desc())\
                            .limit(8).all()
    
    return render_template('knowledge/article_detail.html',
                         article=article,
                         related_articles=related_articles,
                         popular_articles=popular_articles,
                         popular_tags=popular_tags)



@knowledge.route('/tag/<tag_name>')
def tag_articles(tag_name):
    """Articles by tag"""
    tag = KnowledgeTag.query.filter_by(name=tag_name).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('RECORDS_PER_PAGE', 10)
    
    articles = KnowledgeArticle.query\
                              .filter(KnowledgeArticle.tags.contains(tag),
                                     KnowledgeArticle.status == 'published')\
                              .order_by(KnowledgeArticle.published_at.desc())\
                              .paginate(
                                  page=page,
                                  per_page=per_page,
                                  error_out=False
                              )
    
    # 获取热门标签
    popular_tags = db.session.query(KnowledgeTag)\
                            .join(KnowledgeArticle.tags)\
                            .filter(KnowledgeArticle.status == 'published')\
                            .group_by(KnowledgeTag.id)\
                            .order_by(db.func.count(KnowledgeArticle.id).desc())\
                            .limit(10).all()
    
    # 获取最新文章
    recent_articles = KnowledgeArticle.query\
                                     .filter(KnowledgeArticle.status == 'published')\
                                     .order_by(KnowledgeArticle.published_at.desc())\
                                     .limit(5).all()
    
    return render_template('knowledge/tag.html',
                         tag=tag,
                         articles=articles,
                         popular_tags=popular_tags,
                         recent_articles=recent_articles)

# 管理员功能
@knowledge.route('/admin')
@login_required
def admin_index():
    """Knowledge management index (admin)"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    # 获取统计数据
    stats = {
        'total_articles': KnowledgeArticle.query.count(),
        'published_articles': KnowledgeArticle.query.filter_by(status='published').count(),
        'draft_articles': KnowledgeArticle.query.filter_by(status='draft').count(),
        'total_categories': KnowledgeCategory.query.filter_by(is_active=True).count(),
        'total_tags': KnowledgeTag.query.count()
    }
    
    # 获取最新文章
    recent_articles = KnowledgeArticle.query\
                                     .order_by(KnowledgeArticle.created_at.desc())\
                                     .limit(10).all()
    
    return render_template('knowledge/admin/index.html',
                         stats=stats,
                         recent_articles=recent_articles)

@knowledge.route('/admin/articles')
@login_required
def admin_articles():
    """Article management (admin)"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('RECORDS_PER_PAGE', 20)
    status = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    
    query = KnowledgeArticle.query
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            db.or_(
                KnowledgeArticle.title.ilike(f'%{search}%'),
                KnowledgeArticle.content.ilike(f'%{search}%')
            )
        )
    
    articles = query.order_by(KnowledgeArticle.created_at.desc())\
                   .paginate(
                       page=page,
                       per_page=per_page,
                       error_out=False
                   )
    
    return render_template('knowledge/admin/articles.html',
                         articles=articles,
                         current_status=status,
                         search_query=search)

@knowledge.route('/admin/article/new', methods=['GET', 'POST'])
@login_required
def admin_new_article():
    """Create article (admin)"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        # 处理标签
        tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        tags = []
        for tag_name in tag_names:
            tag = KnowledgeTag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = KnowledgeTag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        
        # 生成或使用提供的slug
        article_slug = form.slug.data.strip() if form.slug.data else slugify(form.title.data)
        
        # 确保slug唯一
        base_slug = article_slug
        counter = 1
        while KnowledgeArticle.query.filter_by(slug=article_slug).first():
            article_slug = f"{base_slug}-{counter}"
            counter += 1
        
        # 创建文章
        article = KnowledgeArticle(
            title=form.title.data,
            slug=article_slug,
            content=form.content.data,
            summary=form.summary.data,
            featured_image=form.featured_image.data,
            author_id=current_user.id,
            status=form.status.data,
            is_featured=form.is_featured.data,
            meta_keywords=form.meta_keywords.data,
            meta_description=form.meta_description.data,
            published_at=datetime.now(timezone.utc) if form.status.data == 'published' else None
        )
        
        article.tags = tags
        
        db.session.add(article)
        db.session.commit()
        
        # 记录管理员操作
        AdminLog.log_action(
            user=current_user,
            action='create_article',
            resource_type='knowledge_article',
            resource_id=article.id,
            details={'title': article.title, 'status': article.status},
            request=request
        )
        
        flash(f'Article "{article.title}" created successfully.', 'success')
        return redirect(url_for('knowledge.admin_articles'))
    
    return render_template('knowledge/admin/article_form.html',
                         form=form,
                         title='New Article')

@knowledge.route('/admin/article/<int:id>/view')
@login_required
def admin_view_article(id):
    """View article detail (admin)"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    article = KnowledgeArticle.query.get_or_404(id)
    
    return render_template('knowledge/admin/article_view.html',
                         article=article)

@knowledge.route('/admin/article/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_article(id):
    """Edit article (admin)"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    article = KnowledgeArticle.query.get_or_404(id)
    form = ArticleForm(obj=article)
    form.article_id = id  # 用于slug验证
    
    if form.validate_on_submit():
        # 处理标签
        tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        tags = []
        for tag_name in tag_names:
            tag = KnowledgeTag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = KnowledgeTag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        
        # 生成或使用提供的slug
        new_slug = form.slug.data.strip() if form.slug.data else slugify(form.title.data)
        
        # 确保slug唯一（排除当前文章）
        if new_slug != article.slug:
            base_slug = new_slug
            counter = 1
            while KnowledgeArticle.query.filter_by(slug=new_slug).filter(KnowledgeArticle.id != article.id).first():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
        
        # 更新文章
        old_status = article.status
        article.title = form.title.data
        article.slug = new_slug
        article.content = form.content.data
        article.summary = form.summary.data
        article.featured_image = form.featured_image.data
        article.status = form.status.data
        article.is_featured = form.is_featured.data
        article.meta_keywords = form.meta_keywords.data
        article.meta_description = form.meta_description.data
        article.tags = tags
        article.updated_at = datetime.now(timezone.utc)
        
        # 如果状态从草稿变为发布，设置发布时间
        if old_status != 'published' and form.status.data == 'published':
            article.published_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # 记录管理员操作
        AdminLog.log_action(
            user=current_user,
            action='update_article',
            resource_type='knowledge_article',
            resource_id=article.id,
            details={'title': article.title, 'status': article.status},
            request=request
        )
        
        flash(f'Article "{article.title}" updated successfully.', 'success')
        return redirect(url_for('knowledge.admin_articles'))
    
    # 预填充表单
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in article.tags])
    
    return render_template('knowledge/admin/article_form.html',
                         form=form,
                         article=article,
                         title='Edit Article')

@knowledge.route('/admin/article/<int:id>/toggle-publish', methods=['POST'])
@login_required
def toggle_publish(id):
    """Quick publish/unpublish article (AJAX)"""
    if not current_user.has_admin_permission():
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action'})
    
    article = KnowledgeArticle.query.get_or_404(id)
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['draft', 'published', 'archived']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        old_status = article.status
        article.status = new_status
        article.updated_at = datetime.now(timezone.utc)
        
        # 如果从草稿变为发布，设置发布时间
        if old_status != 'published' and new_status == 'published':
            article.published_at = datetime.now(timezone.utc)
        
        # 记录操作日志（手动创建以避免事务冲突）
        log = AdminLog(
            user_id=current_user.id,
            action='toggle_publish',
            resource_type='knowledge_article',
            resource_id=article.id,
            details={
                'title': article.title,
                'old_status': old_status,
                'new_status': new_status
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
        
        action = 'published' if new_status == 'published' else 'unpublished'
        return jsonify({
            'success': True, 
            'message': f'Article {action} successfully',
            'new_status': new_status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'})

@knowledge.route('/admin/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Upload image for markdown editor"""
    # Check admin permission
    if not current_user.has_admin_permission():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file in request'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'success': False, 'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        import os
        from werkzeug.utils import secure_filename
        from datetime import datetime, timezone
        from app.models import ArticleImage
        
        # Get article_id from request (optional for now, for backward compatibility)
        article_id = request.form.get('article_id', type=int)
        
        # Create upload directory if not exists
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'knowledge')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = secure_filename(file.filename)
        name, ext = os.path.splitext(original_name)
        filename = f"{timestamp}_{name}{ext}"
        
        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Record association if article_id provided
        if article_id:
            image_record = ArticleImage(
                article_id=article_id,
                image_path=f'uploads/knowledge/{filename}',
                filename=filename
            )
            db.session.add(image_record)
            db.session.commit()
        
        # Return URL
        url = url_for('static', filename=f'uploads/knowledge/{filename}')
        
        return jsonify({
            'success': True,
            'url': url,
            'filename': filename
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge.route('/admin/article/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def admin_delete_article(id):
    """删除文章并清理关联图片"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('knowledge.index'))
    
    article = KnowledgeArticle.query.get_or_404(id)
    
    try:
        import os
        from app.models import ArticleImage
        
        # 获取文章关联的所有图片
        images = ArticleImage.query.filter_by(article_id=article.id).all()
        
        # 删除物理文件
        for img in images:
            try:
                file_path = os.path.join(current_app.root_path, 'static', img.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f'Failed to delete image {img.filename}: {str(e)}')
        
        # 记录操作日志
        AdminLog.log_action(
            user=current_user,
            action='delete_article',
            resource_type='knowledge_article',
            resource_id=article.id,
            details={'title': article.title, 'images_count': len(images)},
            request=request
        )
        
        # 删除数据库记录（CASCADE会自动删除 ArticleImage 记录）
        article_title = article.title
        db.session.delete(article)
        db.session.commit()
        
        flash(f'Article "{article_title}" and {len(images)} associated images deleted successfully.', 'success')
        return redirect(url_for('knowledge.admin_articles'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete article: {str(e)}', 'error')
        return redirect(url_for('knowledge.admin_articles'))
