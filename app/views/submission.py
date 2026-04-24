# -*- coding: utf-8 -*-
"""
Submission views
"""
import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import ISElement, SubmissionHistory, AdminLog, PageView
from app.forms.submission import ISElementSubmissionForm, ReviewForm
from app import limiter

submission = Blueprint('submission', __name__)

@submission.route('/')
def index():
    """Submission home - redirect to submit page"""
    return redirect(url_for('submission.submit_element'))

@submission.route('/submit', methods=['GET', 'POST'])
@limiter.limit("10 per hour; 3 per minute", methods=["POST"])
def submit_element():
    """Submit IS element (visitor does not need login)"""
    # log page view (only on GET)
    if request.method == 'GET':
        PageView.log_view(
            page_type='other',
            user=current_user if current_user.is_authenticated else None,
            request=request
        )
    
    form = ISElementSubmissionForm()
    
    if form.validate_on_submit():
        try:
            # check duplicate name
            existing_element = ISElement.query.filter_by(name=form.name.data).first()
            if existing_element:
                flash(f'IS name "{form.name.data}" already exists. Please use another name.', 'error')
                return render_template('submission/submit.html', form=form)
            
            # create new element
            element = ISElement(
                name=form.name.data,
                family=form.family.data,
                group=form.group.data or None,
                mge_type=form.mge_type.data or None,
                host=form.host.data,
                accession_number=form.accession_number.data or None,
                origin=form.origin.data or None,
                transposition=form.transposition.data or None,
                is_length=form.is_length.data,
                le_cleavage_site=form.le_cleavage_site.data or None,
                re_cleavage_site=form.re_cleavage_site.data or None,
                is_sequence=form.is_sequence.data or None,
                orf_number=form.orf_number.data,
                length=form.length.data or None,
                comment=form.comment.data or None,
                references=form.references.data or None,
                # submitter info
                submitter_first_name=form.first_name.data,
                submitter_last_name=form.last_name.data,
                submitter_institution=form.institution.data,
                submitter_department=form.department.data or None,
                submitter_postal_address=form.postal_address.data or None,
                submitter_postal_code=form.postal_code.data or None,
                submitter_country=form.country.data,
                submitter_email=form.email.data,
                submitter_telephone=form.telephone.data or None,
                status='pending',  # pending review
                submitter_id=None,  # visitor
                submission_date=datetime.now(timezone.utc)
            )
            
            db.session.add(element)
            db.session.flush()  # get id
            
            # create submission history
            history = SubmissionHistory(
                is_element_id=element.id,
                submitter_id=None,  # visitor
                action='create',
                new_data=element.to_dict(include_sequences=True),
                status='pending',
                submission_reason=form.submission_reason.data,
                submitted_at=datetime.now(timezone.utc)
            )
            
            db.session.add(history)
            db.session.commit()
            
            # admin log (only for authenticated users)
            try:
                if current_user.is_authenticated:
                    AdminLog.log_action(
                        user=current_user,
                        action='submission_created',
                        resource_type='is_element',
                        resource_id=element.id,
                        details={'message': f'User submitted new IS element: {element.name}'},
                        request=request
                    )
            except Exception:
                pass
            
            flash(f'IS element "{element.name}" submitted successfully! Your data is queued for review. You will be notified by email after review.', 'success')
            
            form = ISElementSubmissionForm()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Failed to submit IS element: {str(e)}')
            flash('Submission failed, please try again later. If the issue persists, contact administrator.', 'error')
    
    # 如果表单验证失败，显示具体错误
    elif request.method == 'POST':
        error_messages = []
        for field, errors in form.errors.items():
            field_label = getattr(form[field], 'label', None)
            field_name = field_label.text if field_label else field
            for error in errors:
                error_messages.append(f"{field_name}: {error}")
        
        if error_messages:
            flash('Please correct the following errors:', 'error')
            for msg in error_messages:
                flash(msg, 'error')
    
    return render_template('submission/submit.html', form=form)

# Admin features
@submission.route('/pending-review')
@login_required
def pending_review():
    """List of pending submissions"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    # pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ISElement.query.filter_by(status='pending')\
        .order_by(ISElement.submission_date.desc())

    pending_submissions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('submission/pending_review.html', 
                         submissions=pending_submissions)

@submission.route('/review/<int:id>', methods=['GET', 'POST'])
@login_required
def review_submission(id):
    """Review submitted data"""
    if not current_user.has_admin_permission():
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    element = ISElement.query.get_or_404(id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        try:
            # 检查是否要拒绝，如果是，检查已拒绝的数量
            if form.status.data == 'rejected':
                rejected_count = ISElement.query.filter_by(status='rejected').count()
                if rejected_count >= 100:
                    flash(f'Cannot reject: There are already {rejected_count} rejected submissions. Please delete some rejected records before rejecting new submissions. Maximum allowed: 100', 'error')
                    return render_template('submission/review.html', element=element, form=form)
            
            old_status = element.status
            element.status = form.status.data
            history = SubmissionHistory(
                is_element_id=element.id,
                submitter_id=None,
                reviewer_id=current_user.id,
                action='update',
                old_data={'status': old_status},
                new_data={'status': form.status.data},
                status=form.status.data,
                review_comment=form.review_notes.data,
                reviewed_at=datetime.now(timezone.utc)
            )
            db.session.add(history)
            db.session.commit()
            AdminLog.log_action(
                user=current_user,
                action='submission_reviewed',
                resource_type='is_element',
                resource_id=element.id,
                details={'name': element.name, 'status': form.status.data},
                request=request
            )
            flash(f'IS element "{element.name}" reviewed. Status updated to: {form.status.data}', 'success')
            return redirect(url_for('submission.pending_review'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Review failed: {str(e)}')
            flash('Review failed, please try again later.', 'error')
    
    return render_template('submission/review.html', element=element, form=form)

@submission.route('/api/validate-name')
def validate_name():
    """Validate if IS element name exists"""
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify({'exists': False})
    existing = ISElement.query.filter_by(name=name).first()
    return jsonify({'exists': existing is not None})
