#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_excel_vs_db.py

比较示例 Excel 文件与数据库运行时 schema（由 scripts/inspect_db.py 生成的 schema.json）

用法:
  python scripts/compare_excel_vs_db.py --excel "本地部署示例数据(1).xlsx" --schema schema.json --out report.json

输出:
  - 在 stdout 打印简要对比结果
  - 将完整对比报告写入 --out 指定的 JSON 文件（默认 compare_report.json）

报告包括:
  - 每个 sheet 的列 -> 对应的 db 列（若有）
  - 未匹配的 Excel 列
  - 类型不匹配示例（如数字列含非整数）
  - 字符串长度超出 VARCHAR 限制的列（包含最大长度）

注意: 该脚本仅做静态字段/长度检查，不会修改数据库。
"""

import argparse
import json
import re
from pathlib import Path
from pprint import pprint

import pandas as pd


def normalize(s):
    return re.sub(r'[^0-9a-z]', '', str(s).lower())


def load_schema(schema_path):
    obj = json.loads(Path(schema_path).read_text(encoding='utf-8'))
    if 'tables' not in obj or 'is_elements' not in obj['tables']:
        raise SystemExit('schema.json must contain tables.is_elements')
    return obj['tables']['is_elements']


def compare(excel_path, schema):
    xls = pd.read_excel(excel_path, sheet_name=None)
    db_cols = schema['columns']
    db_map = {normalize(c['name']): c for c in db_cols}

    report = {'excel_file': str(excel_path), 'sheets': {}}

    for sheet_name, df in xls.items():
        sheet_report = {}
        sheet_report['shape'] = df.shape
        sheet_report['columns'] = list(df.columns)
        sheet_report['head'] = df.head(3).fillna('').to_dict(orient='records')

        mapping = {}
        unmapped = []
        type_issues = []
        length_issues = []

        # build reverse map for detected matches
        matched_db_cols = set()

        for col in df.columns:
            ncol = normalize(col)
            mapped = None
            if ncol in db_map:
                mapped = db_map[ncol]['name']
                matched_db_cols.add(mapped)
            else:
                # fuzzy match: check substring
                for key in db_map:
                    if ncol in key or key in ncol:
                        mapped = db_map[key]['name']
                        matched_db_cols.add(mapped)
                        break
            if mapped:
                mapping[col] = mapped
                dbdef = None
                # find dbdef by name
                for c in db_cols:
                    if c['name'] == mapped:
                        dbdef = c
                        break
                if dbdef:
                    dbtype = dbdef['type']
                    # check varchar length
                    m = re.search(r'VARCHAR\((\d+)\)', dbtype, re.IGNORECASE)
                    if m:
                        limit = int(m.group(1))
                        vals = df[col].dropna().astype(str)
                        maxlen = int(vals.map(len).max()) if len(vals) > 0 else 0
                        if maxlen > limit:
                            length_issues.append({'excel_column': col, 'db_column': mapped, 'max_length': maxlen, 'limit': limit})
                    # check integer compatibility
                    if 'INT' in dbtype.upper():
                        nonints = []
                        for i, v in df[col].dropna().items():
                            s = str(v).strip()
                            if s == '':
                                continue
                            try:
                                f = float(s)
                                if not f.is_integer():
                                    nonints.append({'index': int(i), 'value': v})
                            except Exception:
                                nonints.append({'index': int(i), 'value': v})
                        if nonints:
                            type_issues.append({'excel_column': col, 'db_column': mapped, 'samples': nonints[:5]})
            else:
                unmapped.append(col)

        # Now check DB columns that are not represented in this sheet
        db_cols_names = [c['name'] for c in db_cols]
        db_not_in_excel = [c for c in db_cols_names if c not in matched_db_cols]

        # For matched columns, compute sample statistics summary (nullable ratio, max length, sample values)
        matched_stats = {}
        for excel_col, db_col in mapping.items():
            vals = df[excel_col].dropna()
            total = len(df)
            non_null = len(vals)
            null_ratio = 1 - (non_null / total) if total>0 else None
            sample_vals = list(vals.astype(str).head(5).values)
            maxlen = int(vals.astype(str).map(len).max()) if non_null>0 else 0
            inferred_type = 'text'
            if non_null>0:
                # detect integer-like
                is_int = True
                is_float = True
                for v in vals.astype(str):
                    try:
                        f = float(v)
                        if not float(f).is_integer():
                            is_int = False
                        # keep is_float True
                    except Exception:
                        is_int = False
                        is_float = False
                        break
                if is_int:
                    inferred_type = 'int'
                elif is_float:
                    inferred_type = 'float'
                else:
                    inferred_type = 'text'
            matched_stats[db_col] = {'excel_column': excel_col, 'non_null_count': non_null, 'null_ratio': null_ratio, 'max_sample_length': maxlen, 'inferred_type': inferred_type, 'samples': sample_vals}

        sheet_report['mapping'] = mapping
        sheet_report['unmapped_columns'] = unmapped
        sheet_report['type_issues'] = type_issues
        sheet_report['length_issues'] = length_issues
        sheet_report['db_not_present_in_sheet'] = db_not_in_excel
        sheet_report['matched_column_stats'] = matched_stats
        report['sheets'][sheet_name] = sheet_report
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='示例数据 Excel 文件路径')
    parser.add_argument('--schema', required=True, help='由 scripts/inspect_db.py 生成的 schema.json 路径')
    parser.add_argument('--out', default='compare_report.json', help='输出 JSON 报告路径')
    args = parser.parse_args()

    excel_path = Path(args.excel)
    if not excel_path.exists():
        print('找不到 Excel 文件:', excel_path)
        raise SystemExit(2)
    schema = load_schema(args.schema)
    report = compare(excel_path, schema)

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('比较完成，输出文件:', args.out)
    # 简要打印每个 sheet 的问题统计
    for s, info in report['sheets'].items():
        print(f"\nSheet: {s}    shape={info['shape']}")
        print('  列数:', len(info['columns']))
        print('  未匹配列:', len(info['unmapped_columns']), info['unmapped_columns'][:10])
        print('  类型问题列:', len(info['type_issues']))
        if info['type_issues']:
            print('    示例:', info['type_issues'][:2])
        print('  长度超限列:', len(info['length_issues']))
        if info['length_issues']:
            print('    示例:', info['length_issues'][:2])

    print('\n如需我分析 report.json 的内容，请把该文件内容贴给我，或允许我读取工作区文件。')
