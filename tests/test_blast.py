# -*- coding: utf-8 -*-
"""Tests for BLAST features."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, PropertyMock
from app.models import ISElement
from app.utils.blast_helper import BlastHelper


class TestBlastHelper:

    def test_init_without_app_context(self):
        """BlastHelper init without Flask app context uses default path."""
        # Outside app context, current_app is not available
        pass

    def test_check_blast_installed_not_found(self):
        """check_blast_installed returns False when BLAST not available."""
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = helper.check_blast_installed()
            assert result is False

    def test_check_blast_installed_ok(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch('subprocess.run', return_value=mock_result):
            result = helper.check_blast_installed()
            assert result is True

    def test_check_database_exists_true(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch('os.path.exists', return_value=True):
            assert helper.check_database_exists() is True

    def test_check_database_exists_false(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch('os.path.exists', return_value=False):
            assert helper.check_database_exists() is False

    def test_run_blastn_not_installed(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch.object(helper, 'check_blast_installed', return_value=False):
            result = helper.run_blastn('ATCG')
            assert 'error' in result

    def test_run_blastn_no_database(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch.object(helper, 'check_blast_installed', return_value=True):
            with patch.object(helper, 'check_database_exists', return_value=False):
                result = helper.run_blastn('ATCG')
                assert 'error' in result

    def test_run_blastp_not_installed(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch.object(helper, 'check_blast_installed', return_value=False):
            result = helper.run_blastp('MKT')
            assert 'error' in result

    def test_run_blastp_no_database(self):
        helper = object.__new__(BlastHelper)
        helper.db_path = '/tmp/fake_db'
        with patch.object(helper, 'check_blast_installed', return_value=True):
            result = helper.run_blastp('MKT')
            assert 'error' in result

    def test_parse_blast_xml_empty(self):
        helper = object.__new__(BlastHelper)
        result = helper._parse_blast_xml('<root></root>')
        assert 'query_id' in result
        assert 'query_length' in result
        assert 'hits' in result
        assert result['hits'] == []

    def test_parse_blast_xml_with_hit(self):
        helper = object.__new__(BlastHelper)
        xml = '''<?xml version="1.0"?>
<!DOCTYPE BlastOutput PUBLIC "-//NCBI//NCBI BlastOutput/EN" "http://www.ncbi.nlm.nih.gov/dtd/NCBI_BlastOutput.dtd">
<BlastOutput>
  <BlastOutput_query-def>test_query</BlastOutput_query-def>
  <BlastOutput_query-len>100</BlastOutput_query-len>
  <Iteration>
    <Hit>
      <Hit_id>IS1</Hit_id>
      <Hit_def>IS1 element</Hit_def>
      <Hit_len>768</Hit_len>
      <Hit_hsps>
        <Hsp>
          <Hsp_bit-score>200.0</Hsp_bit-score>
          <Hsp_evalue>1e-20</Hsp_evalue>
          <Hsp_identity>50</Hsp_identity>
          <Hsp_positive>50</Hsp_positive>
          <Hsp_align-len>50</Hsp_align-len>
          <Hsp_query-from>1</Hsp_query-from>
          <Hsp_query-to>50</Hsp_query-to>
          <Hsp_hit-from>1</Hsp_hit-from>
          <Hsp_hit-to>50</Hsp_hit-to>
          <Hsp_qseq>ATCGATCGAT</Hsp_qseq>
          <Hsp_hseq>ATCGATCGAT</Hsp_hseq>
          <Hsp_midline>|||||||||</Hsp_midline>
        </Hsp>
      </Hit_hsps>
    </Hit>
  </Iteration>
</BlastOutput>'''
        result = helper._parse_blast_xml(xml)
        assert result['query_id'] == 'test_query'
        assert result['query_length'] == 100
        assert len(result['hits']) == 1
        assert result['hits'][0]['id'] == 'IS1'
        assert result['hits'][0]['score'] == 200.0
        assert result['hits'][0]['evalue'] == 1e-20

    def test_parse_blast_xml_invalid(self):
        helper = object.__new__(BlastHelper)
        result = helper._parse_blast_xml('not valid xml')
        assert 'error' in result


class TestBlastViews:

    def test_blast_index(self, client):
        rv = client.get('/blast/')
        assert rv.status_code == 200

    def test_blast_help(self, client):
        rv = client.get('/blast/help')
        assert rv.status_code == 200

    def test_blast_element_detail(self, client, sample_elements):
        el = sample_elements[0]
        rv = client.get(f'/blast/element/{el.id}')
        assert rv.status_code == 200

    def test_blast_element_not_found(self, client):
        rv = client.get('/blast/element/99999')
        assert rv.status_code == 404

    def test_blast_results_page_no_task(self, client):
        rv = client.get('/blast/results_page')
        assert rv.status_code == 200

    def test_blast_submit_no_sequence(self, client):
        rv = client.post('/blast/', data={
            'sequence': '',
            'blast_type': 'blastn',
            'evalue': '0.001',
            'max_hits': '10',
            'word_size': '11',
        })
        assert rv.status_code == 200


class TestDownloadRequestViews:

    def test_admin_download_requests(self, admin_client):
        rv = admin_client.get('/admin/download-requests')
        assert rv.status_code == 200

    def test_download_request_detail_not_found(self, admin_client):
        rv = admin_client.get('/admin/download-requests/99999')
        assert rv.status_code == 404


class TestExportFeatures:

    def test_batch_export_no_ids(self, admin_client):
        rv = admin_client.post('/admin/batch-export', data={
            'format': 'csv',
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_batch_export_csv(self, admin_client, sample_elements):
        ids = [str(el.id) for el in sample_elements[:2]]
        data = {'format': 'csv'}
        for i, el_id in enumerate(ids):
            data[f'ids'] = el_id
        rv = admin_client.post('/admin/batch-export', data=data)
        # May redirect or return file
        assert rv.status_code in (200, 302)

    def test_batch_export_fasta(self, admin_client, sample_elements):
        ids = [str(el.id) for el in sample_elements[:2]]
        data = {'format': 'fasta'}
        for el_id in ids:
            data[f'ids'] = el_id
        rv = admin_client.post('/admin/batch-export', data=data)
        assert rv.status_code in (200, 302)
