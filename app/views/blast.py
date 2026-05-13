# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, session, jsonify, current_app
from app.forms.blast import BlastSearchForm
from app.forms.download_request import DownloadRequestForm
from app.utils.blast_helper import BlastHelper
from app.models.is_element import ISElement
from app.models.user import User
from celery.result import AsyncResult
import time

bp = Blueprint('blast', __name__, url_prefix='/blast')


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = BlastSearchForm()
    download_form = DownloadRequestForm()
    admins = User.query.filter(User.role.in_(['root', 'admin'])).order_by(User.username).all()

    if form.validate_on_submit():
        sequence = form.sequence.data
        blast_type = form.blast_type.data
        evalue = float(form.evalue.data)
        max_hits = int(form.max_hits.data)
        word_size = int(form.word_size.data)

        from app.celery_app import make_celery
        celery = make_celery(current_app._get_current_object())

        task = run_blast_task.delay(
            sequence=sequence,
            blast_type=blast_type,
            evalue=evalue,
            max_hits=max_hits,
            word_size=word_size
        )

        return render_template(
            'blast/index.html',
            form=form,
            download_form=download_form,
            admins=admins,
            task_id=task.id,
            blast_type=blast_type
        )

    return render_template(
        'blast/index.html',
        form=form,
        download_form=download_form,
        admins=admins
    )


@bp.route('/result/<task_id>')
def blast_result(task_id):
    task = AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({'state': 'PENDING', 'status': 'BLAST search is queued...'})
    elif task.state == 'STARTED':
        return jsonify({'state': 'STARTED', 'status': 'BLAST search is running...'})
    elif task.state == 'SUCCESS':
        result = task.result
        if 'error' in result:
            return jsonify({'state': 'ERROR', 'status': result['error']})

        elements_with_blast = []
        is_names = []
        blast_info_map = {}
        for hit in result.get('hits', []):
            hit_id = hit['id']
            if '_ORF' in hit_id:
                is_name = hit_id.split('_ORF')[0]
            else:
                is_name = hit_id
            is_names.append(is_name)
            blast_info_map[is_name] = hit

        elements = ISElement.query.filter(ISElement.name.in_(is_names)).all()

        for elem in elements:
            if elem.name in blast_info_map:
                blast_data = blast_info_map[elem.name]
                elements_with_blast.append({
                    'element': {
                        'id': elem.id,
                        'name': elem.name,
                        'family': elem.family,
                        'host': elem.host,
                        'is_length': elem.is_length,
                        'orf1': elem.orf1,
                        'orf2': elem.orf2,
                    },
                    'blast_score': blast_data['score'],
                    'evalue': blast_data['evalue'],
                    'identity_percent': blast_data['identity_percent'],
                    'query_coverage': blast_data['query_coverage'],
                    'hit_coverage': blast_data['hit_coverage'],
                })

        session['last_blast_results'] = result
        session['last_blast_elements'] = elements_with_blast

        return jsonify({
            'state': 'SUCCESS',
            'results': elements_with_blast,
            'total': len(elements_with_blast),
            'query_info': {
                'query_id': result.get('query_id', 'Query'),
                'query_length': result.get('query_length', 0)
            }
        })
    else:
        return jsonify({'state': 'ERROR', 'status': str(task.info)})


@bp.route('/results_page')
def results_page():
    task_id = request.args.get('task_id')
    if not task_id:
        flash('No BLAST task specified', 'warning')
        return render_template('blast/index.html', form=BlastSearchForm())

    form = BlastSearchForm()
    download_form = DownloadRequestForm()
    admins = User.query.filter(User.role.in_(['root', 'admin'])).order_by(User.username).all()

    task = AsyncResult(task_id)
    if task.state != 'SUCCESS':
        return render_template(
            'blast/index.html',
            form=form,
            download_form=download_form,
            admins=admins,
            task_id=task_id
        )

    result = task.result
    if 'error' in result:
        flash(result['error'], 'danger')
        return render_template(
            'blast/index.html',
            form=form,
            download_form=download_form,
            admins=admins
        )

    elements_with_blast = []
    is_names = []
    blast_info_map = {}
    for hit in result.get('hits', []):
        hit_id = hit['id']
        if '_ORF' in hit_id:
            is_name = hit_id.split('_ORF')[0]
        else:
            is_name = hit_id
        is_names.append(is_name)
        blast_info_map[is_name] = hit

    elements = ISElement.query.filter(ISElement.name.in_(is_names)).all()

    for elem in elements:
        if elem.name in blast_info_map:
            blast_data = blast_info_map[elem.name]
            elements_with_blast.append({
                'element': elem,
                'blast_score': blast_data['score'],
                'evalue': blast_data['evalue'],
                'identity_percent': blast_data['identity_percent'],
                'query_coverage': blast_data['query_coverage'],
                'hit_coverage': blast_data['hit_coverage'],
                'query_from': blast_data['query_from'],
                'query_to': blast_data['query_to'],
                'hit_from': blast_data['hit_from'],
                'hit_to': blast_data['hit_to'],
                'query_seq': blast_data['query_seq'],
                'hit_seq': blast_data['hit_seq'],
                'midline': blast_data['midline'],
                'align_len': blast_data['align_len'],
                'identity': blast_data['identity']
            })

    session['last_blast_results'] = result
    flash(f'Found {len(elements_with_blast)} IS elements matching your query', 'success')

    return render_template(
        'blast/index.html',
        form=form,
        download_form=download_form,
        admins=admins,
        results=elements_with_blast,
        query_info=result
    )


@bp.route('/help')
def help():
    return render_template('blast/help.html')


@bp.route('/element/<int:id>')
def element_detail(id):
    element = ISElement.query.get_or_404(id)

    blast_info = None
    last_results = session.get('last_blast_results')
    if last_results and 'hits' in last_results:
        for hit in last_results['hits']:
            if hit['id'] == element.name:
                blast_info = {
                    'query_id': last_results.get('query_id'),
                    'query_length': last_results.get('query_length'),
                    'score': hit['score'],
                    'evalue': hit['evalue'],
                    'identity': hit['identity'],
                    'identity_percent': hit['identity_percent'],
                    'positive': hit.get('positive', hit['identity']),
                    'positive_percent': hit.get('positive_percent', hit['identity_percent']),
                    'align_len': hit['align_len'],
                    'query_coverage': hit['query_coverage'],
                    'hit_coverage': hit['hit_coverage'],
                    'query_from': hit['query_from'],
                    'query_to': hit['query_to'],
                    'hit_from': hit['hit_from'],
                    'hit_to': hit['hit_to'],
                    'query_seq': hit['query_seq'],
                    'hit_seq': hit['hit_seq'],
                    'midline': hit['midline']
                }
                break

    return render_template(
        'blast/element_detail.html',
        element=element,
        blast_info=blast_info
    )


def _run_blast_impl(sequence, blast_type, evalue, max_hits, word_size):
    blast_helper = BlastHelper()
    if blast_type == 'blastn':
        return blast_helper.run_blastn(
            query_sequence=sequence,
            evalue=evalue,
            max_hits=max_hits,
            word_size=word_size
        )
    elif blast_type == 'blastp':
        return blast_helper.run_blastp(
            query_sequence=sequence,
            evalue=evalue,
            max_hits=max_hits
        )
    return {'error': f'Unsupported BLAST type: {blast_type}'}


from celery_worker import celery


@celery.task(bind=True, time_limit=120, soft_time_limit=100)
def run_blast_task(self, sequence, blast_type, evalue, max_hits, word_size):
    self.update_state(state='STARTED', meta={'status': 'Running BLAST...'})
    return _run_blast_impl(sequence, blast_type, evalue, max_hits, word_size)
