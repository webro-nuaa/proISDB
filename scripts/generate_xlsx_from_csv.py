#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单脚本：从 CSV 模板读取表头并生成 XLSX 模板文件
"""
import csv
from openpyxl import Workbook
from pathlib import Path

csv_path = Path('app/static/templates/is_element_template_full.csv')
xlsx_path = Path('app/static/templates/is_element_template_full.xlsx')

if not csv_path.exists():
    print('CSV template not found:', csv_path)
    raise SystemExit(2)

with csv_path.open('r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader, [])

wb = Workbook()
ws = wb.active
ws.append(headers)
wb.save(xlsx_path)
print('Wrote XLSX:', xlsx_path)
