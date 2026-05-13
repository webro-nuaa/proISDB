# -*- coding: utf-8 -*-
"""
BLAST helper - local BLAST+ invocation and result parsing
"""
import os
import tempfile
import subprocess
from xml.etree import ElementTree as ET
from flask import current_app


class BlastHelper:
    """Local BLAST+ helper class"""
    
    def __init__(self, db_path=None):
        """
        初始化BLAST工具
        
        Args:
            db_path: BLAST数据库路径，默认为blast_db/is_elements
        """
        if db_path is None:
            # 使用项目根目录下的blast_db
            db_path = os.path.join(
                current_app.root_path, '..', 'blast_db', 'is_elements'
            )
        self.db_path = db_path
    
    def check_blast_installed(self):
        """Check if BLAST+ is installed"""
        try:
            result = subprocess.run(
                ['blastn', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_database_exists(self):
        """Check if BLAST database exists"""
        # 检查至少一个数据库文件存在
        extensions = ['.nhr', '.nin', '.nsq']
        return any(
            os.path.exists(f"{self.db_path}{ext}") 
            for ext in extensions
        )
    
    def run_blastn(self, query_sequence, evalue=10, max_hits=50, word_size=11):
        """
        Run blastn nucleotide alignment
        
        Args:
            query_sequence: 查询序列（FASTA格式或纯序列）
            evalue: E-value阈值，默认10
            max_hits: 最大返回结果数，默认50
            word_size: 词长度，默认11（短序列可用7）
        
        Returns:
            dict: 解析后的BLAST结果
        """
        # 检查BLAST是否安装
        if not self.check_blast_installed():
            return {
                'error': 'BLAST+未安装。请运行: sudo apt install ncbi-blast+'
            }
        
        # 检查数据库是否存在
        if not self.check_database_exists():
            return {
                'error': f'BLAST数据库不存在: {self.db_path}。请运行build_blast_db.py创建数据库'
            }
        
        # 创建临时文件保存查询序列
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as query_file:
            # 如果输入不是FASTA格式，添加header
            if not query_sequence.strip().startswith('>'):
                query_file.write('>Query\n')
            query_file.write(query_sequence)
            query_file_path = query_file.name
        
        try:
            # 运行blastn
            cmd = [
                'blastn',
                '-query', query_file_path,
                '-db', self.db_path,
                '-outfmt', '5',  # XML格式
                '-evalue', str(evalue),
                '-max_target_seqs', str(max_hits),
                '-word_size', str(word_size)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
            )
            
            if result.returncode != 0:
                return {
                    'error': f'BLAST运行失败: {result.stderr}'
                }
            
            # 解析XML结果
            return self._parse_blast_xml(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {'error': 'BLAST运行超时（>60秒），请减少查询序列长度或降低max_hits'}
        except Exception as e:
            return {'error': f'BLAST运行错误: {str(e)}'}
        finally:
            # 清理临时文件
            if os.path.exists(query_file_path):
                os.remove(query_file_path)
    
    def run_blastp(self, query_sequence, evalue=10, max_hits=50):
        """
        Run blastp protein alignment
        
        Args:
            query_sequence: 查询序列（FASTA格式或纯序列）
            evalue: E-value阈值
            max_hits: 最大返回结果数
        
        Returns:
            dict: 解析后的BLAST结果
        """
        # 检查BLAST是否安装
        if not self.check_blast_installed():
            return {
                'error': 'BLAST+未安装。请运行: sudo apt install ncbi-blast+'
            }
        
        # 蛋白数据库路径（使用_prot后缀）
        protein_db_path = self.db_path + '_prot'
        
        # 检查蛋白数据库是否存在
        extensions = ['.phr', '.pin', '.psq']
        if not any(os.path.exists(f"{protein_db_path}{ext}") for ext in extensions):
            return {
                'error': f'蛋白BLAST数据库不存在: {protein_db_path}。请运行build_blast_db.py创建数据库'
            }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as query_file:
            if not query_sequence.strip().startswith('>'):
                query_file.write('>Query\n')
            query_file.write(query_sequence)
            query_file_path = query_file.name
        
        try:
            cmd = [
                'blastp',
                '-query', query_file_path,
                '-db', protein_db_path,
                '-outfmt', '5',
                '-evalue', str(evalue),
                '-max_target_seqs', str(max_hits)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {'error': f'BLAST运行失败: {result.stderr}'}
            
            return self._parse_blast_xml(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {'error': 'BLAST运行超时'}
        except Exception as e:
            return {'error': f'BLAST运行错误: {str(e)}'}
        finally:
            if os.path.exists(query_file_path):
                os.remove(query_file_path)
    
    def _parse_blast_xml(self, xml_string):
        """
        Parse BLAST XML results
        
        Args:
            xml_string: BLAST输出的XML字符串
        
        Returns:
            dict: 包含查询信息和hit列表的字典
        """
        try:
            root = ET.fromstring(xml_string)
            
            # Get query info
            query_def = root.find('.//BlastOutput_query-def')
            query_len = root.find('.//BlastOutput_query-len')
            
            result = {
                'query_id': query_def.text if query_def is not None else 'Query',
                'query_length': int(query_len.text) if query_len is not None else 0,
                'hits': []
            }
            
            # Parse all hits
            for hit in root.findall('.//Hit'):
                hit_id = hit.find('Hit_id').text
                hit_def = hit.find('Hit_def').text
                hit_len = int(hit.find('Hit_len').text)
                
                # Parse HSP (High-scoring Segment Pair)
                hsps = []
                for hsp in hit.findall('.//Hsp'):
                    hsp_data = {
                        'score': float(hsp.find('Hsp_bit-score').text),
                        'evalue': float(hsp.find('Hsp_evalue').text),
                        'identity': int(hsp.find('Hsp_identity').text),
                        'positive': int(hsp.find('Hsp_positive').text) if hsp.find('Hsp_positive') is not None else int(hsp.find('Hsp_identity').text),
                        'align_len': int(hsp.find('Hsp_align-len').text),
                        'query_from': int(hsp.find('Hsp_query-from').text),
                        'query_to': int(hsp.find('Hsp_query-to').text),
                        'hit_from': int(hsp.find('Hsp_hit-from').text),
                        'hit_to': int(hsp.find('Hsp_hit-to').text),
                        'query_seq': hsp.find('Hsp_qseq').text,
                        'hit_seq': hsp.find('Hsp_hseq').text,
                        'midline': hsp.find('Hsp_midline').text
                    }
                    
                    # Calculate percentages
                    hsp_data['identity_percent'] = round(
                        (hsp_data['identity'] / hsp_data['align_len']) * 100, 2
                    )
                    hsp_data['positive_percent'] = round(
                        (hsp_data['positive'] / hsp_data['align_len']) * 100, 2
                    )
                    
                    # Calculate coverage
                    hsp_data['query_coverage'] = round(
                        (abs(hsp_data['query_to'] - hsp_data['query_from']) + 1) / result['query_length'] * 100, 2
                    )
                    hsp_data['hit_coverage'] = round(
                        (abs(hsp_data['hit_to'] - hsp_data['hit_from']) + 1) / hit_len * 100, 2
                    )
                    
                    hsps.append(hsp_data)
                
                # Take best HSP only
                if hsps:
                    best_hsp = max(hsps, key=lambda x: x['score'])
                    result['hits'].append({
                        'id': hit_id,
                        'name': hit_def,
                        'length': hit_len,
                        **best_hsp
                    })
            
            return result
            
        except Exception as e:
            return {'error': f'解析BLAST结果失败: {str(e)}'}
