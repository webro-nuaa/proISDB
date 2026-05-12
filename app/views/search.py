# -*- coding: utf-8 -*-
"""
搜索功能视图
"""
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import ISElement, PageView, SearchLog, User
from app.models import DownloadRequest, DownloadRequestItem
from app.forms.download_request import DownloadRequestForm
from sqlalchemy.orm import load_only
from app.forms.search import SearchForm, AdvancedSearchForm
from app.utils.helpers import escape_like


search = Blueprint('search', __name__)

@search.route('/')
def index():
    """搜索页面 - 支持简单搜索和高级搜索"""
    form = SearchForm()
    advanced_form = AdvancedSearchForm()
    
    # 记录页面访问
    PageView.log_view(
        page_type='search',
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('SEARCH_RESULTS_PER_PAGE', 10)
    
    # 检查是否是高级搜索
    is_advanced = request.args.get('advanced') == '1'
    
    if is_advanced:
        # 高级搜索逻辑
        search_params = {
            'name': request.args.get('name', '').strip(),
            'name_match': request.args.get('name_match', 'contains'),
            'family': request.args.get('family', ''),
            'family_match': request.args.get('family_match', 'contains'),
            'origin': request.args.get('origin', '').strip(),
            'origin_match': request.args.get('origin_match', 'contains'),
            'mge_type': request.args.get('mge_type', '').strip(),
            'mge_type_match': request.args.get('mge_type_match', 'contains'),
            'group': request.args.get('group', '').strip(),
            'group_match': request.args.get('group_match', 'contains'),
            'host': request.args.get('host', '').strip(),
            'accession': request.args.get('accession', '').strip(),
            'accession_match': request.args.get('accession_match', 'contains'),

            'length_field': request.args.get('length_field', '').strip(),
            'length_match': request.args.get('length_match', 'equal_to'),

        }
        
        search_conditions = []
        has_search_criteria = any(v for k, v in search_params.items() if v and not k.endswith('_match'))
        
        if has_search_criteria:
            # 只有有搜索条件时才进行查询
            query = ISElement.query.filter_by(status='approved')
            # 仅加载用于表格展示或筛选的必要字段，减少查询开销
            query = query.options(load_only(
                ISElement.id, ISElement.name, ISElement.family, ISElement.group, ISElement.mge_type, ISElement.host,
                ISElement.synomyns, ISElement.isoform, ISElement.iso, ISElement.origin,
                ISElement.is_length, ISElement.length, ISElement.orf_number, ISElement.orf1, ISElement.orf2, ISElement.accession_number,
                ISElement.le_cleavage_site, ISElement.re_cleavage_site,
                ISElement.submitter_first_name, ISElement.submitter_last_name, ISElement.submitter_email,
                ISElement.created_at, ISElement.status, ISElement.comment
            ))
            
            # 处理name字段匹配
            if search_params['name']:
                name_value = search_params['name']
                name_match = search_params['name_match']
                safe_name = escape_like(name_value)
                if name_match == 'contains':
                    query = query.filter(ISElement.name.contains(safe_name))
                elif name_match == 'begin_with':
                    query = query.filter(ISElement.name.startswith(safe_name))
                elif name_match == 'end_with':
                    query = query.filter(ISElement.name.endswith(safe_name))
                elif name_match == 'equal_to':
                    query = query.filter(ISElement.name == name_value)
                search_conditions.append(f"name({name_match}):{name_value}")
            
            # 处理family字段匹配
            if search_params['family']:
                family_value = search_params['family']
                family_match = search_params['family_match']
                safe_family = escape_like(family_value)
                if family_match == 'contains':
                    query = query.filter(ISElement.family.contains(safe_family))
                elif family_match == 'begin_with':
                    query = query.filter(ISElement.family.startswith(safe_family))
                elif family_match == 'end_with':
                    query = query.filter(ISElement.family.endswith(safe_family))
                elif family_match == 'equal_to':
                    query = query.filter(ISElement.family == family_value)
                search_conditions.append(f"family({family_match}):{family_value}")
            
            # 处理origin字段匹配
            if search_params['origin']:
                origin_value = search_params['origin']
                origin_match = search_params['origin_match']
                safe_origin = escape_like(origin_value)
                if origin_match == 'contains':
                    query = query.filter(ISElement.origin.contains(safe_origin))
                elif origin_match == 'begin_with':
                    query = query.filter(ISElement.origin.startswith(safe_origin))
                elif origin_match == 'end_with':
                    query = query.filter(ISElement.origin.endswith(safe_origin))
                elif origin_match == 'equal_to':
                    query = query.filter(ISElement.origin == origin_value)
                search_conditions.append(f"origin({origin_match}):{origin_value}")
            
            # 处理MGE类型
            if search_params['mge_type']:
                mge_type_value = search_params['mge_type']
                mge_type_match = search_params['mge_type_match']
                safe_mge = escape_like(mge_type_value)
                if mge_type_match == 'contains':
                    query = query.filter(ISElement.mge_type.contains(safe_mge))
                elif mge_type_match == 'begin_with':
                    query = query.filter(ISElement.mge_type.startswith(safe_mge))
                elif mge_type_match == 'end_with':
                    query = query.filter(ISElement.mge_type.endswith(safe_mge))
                elif mge_type_match == 'equal_to':
                    query = query.filter(ISElement.mge_type == mge_type_value)
                search_conditions.append(f"mge_type({mge_type_match}):{mge_type_value}")
            
            # 处理group字段匹配
            if search_params['group']:
                group_value = search_params['group']
                group_match = search_params['group_match']
                safe_group = escape_like(group_value)
                if group_match == 'contains':
                    query = query.filter(ISElement.group.contains(safe_group))
                elif group_match == 'begin_with':
                    query = query.filter(ISElement.group.startswith(safe_group))
                elif group_match == 'end_with':
                    query = query.filter(ISElement.group.endswith(safe_group))
                elif group_match == 'equal_to':
                    query = query.filter(ISElement.group == group_value)
                search_conditions.append(f"group({group_match}):{group_value}")
            
            if search_params['host']:
                query = query.filter(ISElement.host.contains(escape_like(search_params['host'])))
                search_conditions.append(f"host:{search_params['host']}")
            
            # 处理accession字段匹配
            if search_params['accession']:
                accession_value = search_params['accession']
                accession_match = search_params['accession_match']
                safe_accession = escape_like(accession_value)
                if accession_match == 'contains':
                    query = query.filter(ISElement.accession_number.contains(safe_accession))
                elif accession_match == 'begin_with':
                    query = query.filter(ISElement.accession_number.startswith(safe_accession))
                elif accession_match == 'end_with':
                    query = query.filter(ISElement.accession_number.endswith(safe_accession))
                elif accession_match == 'equal_to':
                    query = query.filter(ISElement.accession_number == accession_value)
                search_conditions.append(f"accession({accession_match}):{accession_value}")
            
            # 处理 length 字段（蛋白质长度）
            if search_params['length_field']:
                try:
                    length_value = int(search_params['length_field'])
                    length_match = search_params['length_match']
                    if length_match == 'equal_to':
                        query = query.filter(ISElement.length == length_value)
                    elif length_match == 'gte':
                        query = query.filter(ISElement.length >= length_value)
                    elif length_match == 'lte':
                        query = query.filter(ISElement.length <= length_value)
                    search_conditions.append(f"length({length_match}):{length_value}")
                except ValueError:
                    pass  # 忽略无效的数字输入
            

        else:
            # 未搜索时返回空结果
            query = ISElement.query.filter_by(id=-1)
        
        search_term = ' '.join(search_conditions) if search_conditions else ''
        search_type = 'advanced'
        
        # 预填充高级搜索表单
        for field_name, value in search_params.items():
            if hasattr(advanced_form, field_name) and value:
                getattr(advanced_form, field_name).data = value

    else:
        query_text = request.args.get('query', '').strip()
        search_params = {'query': query_text}

        if query_text:
            query = ISElement.query.filter_by(status='approved')
            query = query.options(load_only(
                ISElement.id, ISElement.name, ISElement.family, ISElement.group, ISElement.mge_type, ISElement.host,
                ISElement.synomyns, ISElement.isoform, ISElement.iso, ISElement.origin,
                ISElement.is_length, ISElement.length, ISElement.orf_number, ISElement.orf1, ISElement.orf2, ISElement.accession_number,
                ISElement.le_cleavage_site, ISElement.re_cleavage_site,
                ISElement.submitter_first_name, ISElement.submitter_last_name, ISElement.submitter_email,
                ISElement.created_at, ISElement.status, ISElement.comment
            ))
            safe_q = escape_like(query_text)
            search_filter = db.or_(
                ISElement.name.contains(safe_q),
                ISElement.family.contains(safe_q),
                ISElement.host.contains(safe_q),
                ISElement.origin.contains(safe_q),
                ISElement.group.contains(safe_q),
                ISElement.comment.contains(safe_q),
                ISElement.accession_number.contains(safe_q)
            )
            query = query.filter(search_filter)
        else:
            query = ISElement.query.filter_by(id=-1)

        search_term = query_text
        search_type = 'simple'

        form.query.data = query_text
    
    # 排序和分页
    results = query.order_by(ISElement.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 记录搜索日志
    if search_term:
        SearchLog.log_search(
            search_term=search_term,
            search_type=f'is_elements_{search_type}',
            results_count=results.total,
            user=current_user if current_user.is_authenticated else None,
            request=request
        )
    
    # get admin list for assign-to dropdown
    admins = User.query.filter(User.role.in_(['root','admin'])).order_by(User.username).all()

    return render_template('search/index.html',
                         form=form,
                         advanced_form=advanced_form,
                         results=results,
                         search_params=search_params,
                         is_advanced=is_advanced,
                         admins=admins)


@search.route('/apply-download', methods=['POST'])
def apply_download():
    """Handle visitor download requests (batch) - available to all users (logged in or not)"""
    # selected ids expected as comma-separated string
    selected = request.form.get('selected_ids', '')
    if not selected:
        flash('未选择任何条目。', 'error')
        return redirect(url_for('search.index'))

    try:
        ids = [int(x) for x in selected.split(',') if x.strip()]
    except ValueError:
        flash('选择条目无效。', 'error')
        return redirect(url_for('search.index'))

    # build form and validate
    form = DownloadRequestForm()
    # populate admin choices
    admins = User.query.filter(User.role.in_(['root','admin'])).order_by(User.username).all()
    form.assigned_admin.choices = [(a.id, a.username) for a in admins]

    if form.validate_on_submit():
        # create request
        dr = DownloadRequest(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.strip(),
            institution=form.institution.data.strip(),
            department=form.department.data.strip() if form.department.data else None,
            country=form.country.data.strip(),
            reason=form.reason.data.strip(),
            format=form.format.data or 'csv',  # 保存导出格式
            assigned_admin_id=form.assigned_admin.data,
            status='pending',
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(dr)
        db.session.flush()

        for is_id in ids:
            item = DownloadRequestItem(request_id=dr.id, is_element_id=is_id)
            db.session.add(item)

        db.session.commit()

        flash('Application submitted successfully.', 'success')
        return redirect(url_for('search.index'))
    else:
        # show form errors
        for field, errs in form.errors.items():
            for e in errs:
                flash(f"{field}: {e}", 'error')
        return redirect(url_for('search.index'))

@search.route('/advanced')
def advanced():
    """高级搜索页面"""
    form = AdvancedSearchForm()
    
    PageView.log_view(
        page_type='search',
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('SEARCH_RESULTS_PER_PAGE', 10)
    
    # 获取所有搜索参数
    params = {
        'name': request.args.get('name', '').strip(),
        'family': request.args.get('family', ''),
        'group': request.args.get('group', '').strip(),
        'host': request.args.get('host', '').strip(),
        'accession': request.args.get('accession', '').strip(),
        'orf_function': request.args.get('orf_function', '').strip(),
        'min_length': request.args.get('min_length', type=int),
        'max_length': request.args.get('max_length', type=int)
    }
    
    # 构建查询
    query = ISElement.query.filter_by(status='approved')
    # 仅加载表格需要的字段以优化性能
    query = query.options(load_only(
        ISElement.id, ISElement.name, ISElement.family, ISElement.group, ISElement.mge_type, ISElement.host,
        ISElement.synomyns, ISElement.isoform, ISElement.iso, ISElement.origin,
    ISElement.is_length, ISElement.length, ISElement.orf_number, ISElement.orf1, ISElement.orf2, ISElement.accession_number,
        ISElement.le_cleavage_site, ISElement.re_cleavage_site,
        ISElement.submitter_first_name, ISElement.submitter_last_name, ISElement.submitter_email,
        ISElement.created_at, ISElement.status, ISElement.comment
    ))
    
    if params['name']:
        query = query.filter(ISElement.name.contains(params['name']))
    
    if params['family']:
        query = query.filter_by(family=params['family'])
    
    if params['group']:
        query = query.filter(ISElement.group.contains(params['group']))
    
    if params['host']:
        query = query.filter(ISElement.host.contains(params['host']))
    
    if params['accession']:
        query = query.filter(ISElement.accession_number.contains(params['accession']))
    
    if params['orf_function']:
        query = query.filter(ISElement.orf_1_function.contains(escape_like(params['orf_function'])))
    
    if params['min_length']:
        query = query.filter(ISElement.is_length >= params['min_length'])
    
    if params['max_length']:
        query = query.filter(ISElement.is_length <= params['max_length'])
    
    # 排序和分页
    results = query.order_by(ISElement.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 记录搜索日志
    if any(v for v in params.values() if v):
        search_term = ' '.join(f"{k}:{v}" for k, v in params.items() if v)
        SearchLog.log_search(
            search_term=search_term,
            search_type='is_elements',
            results_count=results.total,
            user=current_user if current_user.is_authenticated else None,
            request=request
        )
    
    # 预填充表单
    for field_name, value in params.items():
        if hasattr(form, field_name) and value:
            getattr(form, field_name).data = value
    
    return render_template('search/advanced.html',
                         form=form,
                         results=results,
                         search_params=params)

@search.route('/element/<int:id>')
def element_detail(id):
    """IS元素详情页面"""
    element = ISElement.query.filter_by(id=id, status='approved').first_or_404()
    
    # 记录页面访问
    PageView.log_view(
        page_type='is_element',
        page_id=id,
        user=current_user if current_user.is_authenticated else None,
        request=request
    )
    
    # 获取相关IS元素（同家族的其他元素）
    related_elements = ISElement.query.filter(
        ISElement.family == element.family,
        ISElement.id != element.id,
        ISElement.status == 'approved'
    ).limit(5).all()
    
    return render_template('search/element_detail.html',
                         element=element,
                         related_elements=related_elements)

@search.route('/api/suggestions')
def api_suggestions():
    """搜索建议API"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    safe_q = escape_like(query)
    name_suggestions = db.session.query(ISElement.name)\
                                .filter(ISElement.name.contains(safe_q))\
                                .filter_by(status='approved')\
                                .distinct().limit(5).all()
    
    host_suggestions = db.session.query(ISElement.host)\
                                .filter(ISElement.host.contains(safe_q))\
                                .filter_by(status='approved')\
                                .distinct().limit(5).all()
    
    suggestions = []
    suggestions.extend([{'text': name[0], 'type': 'name'} for name in name_suggestions])
    suggestions.extend([{'text': host[0], 'type': 'host'} for host in host_suggestions])
    
    return jsonify(suggestions[:10])

@search.route('/api/families')
def api_families():
    """获取IS家族列表API"""
    families = db.session.query(ISElement.family)\
                        .filter_by(status='approved')\
                        .distinct()\
                        .order_by(ISElement.family)\
                        .all()
    
    return jsonify([family[0] for family in families])

@search.route('/export')
def export_results():
    """导出搜索结果"""
    # 这里可以实现CSV/Excel导出功能
    # 暂时返回JSON格式
    
    # 重新构建查询（复用搜索逻辑）
    query_text = request.args.get('query', '').strip()
    family = request.args.get('family', '')
    host = request.args.get('host', '').strip()
    
    query = ISElement.query.filter_by(status='approved')
    
    if query_text:
        safe_q = escape_like(query_text)
        search_filter = db.or_(
            ISElement.name.contains(safe_q),
            ISElement.family.contains(safe_q),
            ISElement.host.contains(safe_q),
            ISElement.orf_1_function.contains(safe_q)
        )
        query = query.filter(search_filter)
    
    if family:
        query = query.filter_by(family=family)
    
    if host:
        safe_host = escape_like(host)
        query = query.filter(ISElement.host.contains(safe_host))
    
    results = query.limit(1000).all()
    
    data = []
    for element in results:
        data.append({
            'name': element.name,
            'family': element.family,
            'host': element.host,
            'length': element.is_length,
            'accession': element.accession_number,
            'orf_1_function': element.orf_1_function
        })
    
    return jsonify({
        'count': len(data),
        'data': data
    })
