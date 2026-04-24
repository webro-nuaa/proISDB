# -*- coding: utf-8 -*-
"""
FASTA格式生成工具
"""

def generate_fasta(elements, include_orfs=True):
    """
    将IS元素列表转换为FASTA格式
    
    Args:
        elements: ISElement对象列表
        include_orfs: 是否包含ORF序列
    
    Returns:
        str: FASTA格式的字符串
    """
    fasta_lines = []
    
    for elem in elements:
        # 主IS序列
        if elem.is_sequence:
            # 构建header
            header_parts = [elem.name or f'IS_{elem.id}']
            
            # 添加描述信息
            desc_parts = []
            if elem.family:
                desc_parts.append(f'family={elem.family}')
            if elem.group:
                desc_parts.append(f'group={elem.group}')
            if elem.origin:
                desc_parts.append(f'origin={elem.origin}')
            if elem.host:
                desc_parts.append(f'host={elem.host}')
            if elem.is_length or elem.length:
                length = elem.is_length or elem.length
                desc_parts.append(f'length={length}')
            if elem.accession_number:
                desc_parts.append(f'accession={elem.accession_number}')
            
            header = '>' + header_parts[0]
            if desc_parts:
                header += ' ' + '|'.join(desc_parts)
            
            fasta_lines.append(header)
            # 序列每行60个字符
            sequence = elem.is_sequence.strip()
            for i in range(0, len(sequence), 60):
                fasta_lines.append(sequence[i:i+60])
            
            fasta_lines.append('')  # 空行分隔
        
        # ORF序列
        if include_orfs:
            # ORF1
            if elem.orf_1_sequence:
                header_parts = [f'{elem.name or f"IS_{elem.id}"}_ORF1']
                desc_parts = []
                
                if elem.orf_1_function:
                    desc_parts.append(f'function={elem.orf_1_function}')
                if elem.orf_1_length:
                    desc_parts.append(f'length={elem.orf_1_length}')
                if elem.orf_1_begin and elem.orf_1_end:
                    desc_parts.append(f'position={elem.orf_1_begin}..{elem.orf_1_end}')
                if elem.orf_1_strand:
                    desc_parts.append(f'strand={elem.orf_1_strand}')
                
                header = '>' + header_parts[0]
                if desc_parts:
                    header += ' ' + '|'.join(desc_parts)
                
                fasta_lines.append(header)
                sequence = elem.orf_1_sequence.strip()
                for i in range(0, len(sequence), 60):
                    fasta_lines.append(sequence[i:i+60])
                fasta_lines.append('')
            
            # ORF2
            if elem.orf_2_sequence:
                header_parts = [f'{elem.name or f"IS_{elem.id}"}_ORF2']
                desc_parts = []
                
                if elem.orf_2_function:
                    desc_parts.append(f'function={elem.orf_2_function}')
                if elem.orf_2_length:
                    desc_parts.append(f'length={elem.orf_2_length}')
                if elem.orf_2_begin and elem.orf_2_end:
                    desc_parts.append(f'position={elem.orf_2_begin}..{elem.orf_2_end}')
                if elem.orf_2_strand:
                    desc_parts.append(f'strand={elem.orf_2_strand}')
                
                header = '>' + header_parts[0]
                if desc_parts:
                    header += ' ' + '|'.join(desc_parts)
                
                fasta_lines.append(header)
                sequence = elem.orf_2_sequence.strip()
                for i in range(0, len(sequence), 60):
                    fasta_lines.append(sequence[i:i+60])
                fasta_lines.append('')
    
    return '\n'.join(fasta_lines)
