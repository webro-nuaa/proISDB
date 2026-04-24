# -*- coding: utf-8 -*-
"""
用户认证视图
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, AdminLog
from app.forms.auth import LoginForm, ChangePasswordForm, ProfileForm

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.verify_password(form.password.data):
            if not user.is_active:
                flash('Your account has been disabled. Please contact the administrator.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # 记录登录日志
            if user.has_admin_permission():
                AdminLog.log_action(
                    user=user,
                    action='login',
                    resource_type='user',
                    resource_id=user.id,
                    request=request
                )
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Incorrect username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """用户登出"""
    # 记录登出日志
    if current_user.has_admin_permission():
        AdminLog.log_action(
            user=current_user,
            action='logout',
            resource_type='user',
            resource_id=current_user.id,
            request=request
        )
    
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    """用户资料页面"""
    return render_template('auth/profile.html', user=current_user)

@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑用户资料"""
    form = ProfileForm(current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.institution = form.institution.data
        current_user.department = form.department.data
        current_user.country = form.country.data
        current_user.telephone = form.telephone.data
        current_user.email = form.email.data
        current_user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
    
    # 预填充表单
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.institution.data = current_user.institution
    form.department.data = current_user.department
    form.country.data = current_user.country
    form.telephone.data = current_user.telephone
    form.email.data = current_user.email
    
    return render_template('auth/edit_profile.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # 记录密码修改日志
            if current_user.has_admin_permission():
                AdminLog.log_action(
                    user=current_user,
                    action='change_password',
                    resource_type='user',
                    resource_id=current_user.id,
                    request=request
                )
            
            flash('Password changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth.before_request
def before_request():
    """请求前处理"""
    # 记录页面访问
    from app.models import PageView
    if request.endpoint and not request.endpoint.startswith('static') and not request.endpoint.startswith('auth.'):
        try:
            PageView.log_view(
                page_type='auth',
                user=current_user if current_user.is_authenticated else None,
                request=request
            )
        except Exception as e:
            # 记录日志但不影响页面访问
            print(f"PageView记录失败: {e}")

@auth.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    """邮箱验证页面"""
    from app.forms.email_verification import SendVerificationCodeForm, VerifyEmailForm
    from app.models.email_verification import EmailVerification
    from app.utils.email_service import EmailService
    
    send_form = SendVerificationCodeForm()
    verify_form = VerifyEmailForm()
    
    # 处理发送验证码请求
    if send_form.validate_on_submit() and request.form.get('action') == 'send':
        email = send_form.email.data
        
        # 创建验证码记录
        verification = EmailVerification(
            user_id=current_user.id,
            email=email,
            purpose='email_change',
            validity_minutes=15
        )
        
        db.session.add(verification)
        db.session.commit()
        
        # 发送验证码邮件
        success, message = EmailService.send_verification_code(
            to_email=email,
            verification_code=verification.verification_code,
            purpose='email_change',
            username=current_user.username
        )
        
        if success:
            flash(f'Verification code has been sent to {email}. Please check your inbox.', 'success')
            session['verification_email'] = email
        else:
            flash(f'Failed to send verification code: {message}', 'error')
            db.session.delete(verification)
            db.session.commit()
        
        return redirect(url_for('auth.verify_email'))
    
    # 处理验证码验证请求
    if verify_form.validate_on_submit() and request.form.get('action') == 'verify':
        # 从session获取邮箱
        email = session.get('verification_email')
        
        if not email:
            flash('Please send verification code first.', 'error')
            return redirect(url_for('auth.verify_email'))
        
        code = verify_form.verification_code.data
        
        # 查找最新的未验证的验证码
        verification = EmailVerification.query.filter_by(
            user_id=current_user.id,
            email=email,
            is_verified=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification:
            flash('No verification code found. Please send a new code.', 'error')
            return redirect(url_for('auth.verify_email'))
        
        # 验证验证码
        success, message = verification.verify(code)
        db.session.commit()
        
        if success:
            # 更新用户邮箱
            current_user.email = email
            current_user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # 记录日志
            if current_user.has_admin_permission():
                AdminLog.log_action(
                    user=current_user,
                    action='email_verified',
                    resource_type='user',
                    resource_id=current_user.id,
                    details={'email': email},
                    request=request
                )
            
            flash('Email verified and saved successfully!', 'success')
            session.pop('verification_email', None)
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_email.html', 
                         send_form=send_form, 
                         verify_form=verify_form)
