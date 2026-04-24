#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据当前示例数据（Excel），生成覆盖重建 `is_elements` 表的 SQL。

用法:
  python scripts/recreate_is_elements.py --excel "本地部署示例数据(1).xlsx" --out sql/recreate_is_elements.sql

脚本会：
 - 读取 Excel（默认读取第一个非空 sheet）并推断每列的数据类型/长度
 - 生成一份 SQL：先将现有 `is_elements` 重命名为备份表（带时间戳），再创建新的 `is_elements` 表
 - 不会直接修改数据库；要在数据库上执行生成的 SQL，请在了解风险后运行

注意：脚本保留了若干管理字段（id, created_at, updated_at, status）以兼容应用逻辑。
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def normalize_col(s):
    s = str(s).strip()
    # replace spaces and punctuation with underscore, keep alnum and _
    s = re.sub(r"[^0-9a-zA-Z]+", '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    # lower case
    return s.lower() or 'col'


def infer_type(series):
    vals = series.dropna().astype(str)
    if len(vals) == 0:
        return 'varchar', 255
    maxlen = int(vals.map(len).max())
    # very long sequences -> LONGTEXT
    if maxlen > 10000:
        return 'longtext', None
    # long sequences -> TEXT threshold
    if maxlen > 1000:
        return 'text', None
    # check integer
    is_int = True
    is_float = True
    for v in vals:
        vs = v.strip()
        if vs == '':
            continue
        try:
            f = float(vs)
            if not float(f).is_integer():
                is_int = False
        except Exception:
            is_int = False
            is_float = False
            break
    if is_int and len(vals) > 0 and maxlen < 20:
        return 'int', None
    # short strings -> varchar sizing
    if maxlen <= 50:
        return 'varchar', max(64, ( (maxlen//10 + 1) * 16 ))
    if maxlen <= 255:
        return 'varchar', min(255, maxlen*2)
    return 'text', None


def build_table_sql(col_defs, table_name='is_elements'):
    lines = []
    lines.append(f'CREATE TABLE `{table_name}` (')
    # id
    lines.append('  `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,')
    for name, (ctype, clen) in col_defs.items():
        if ctype == 'longtext':
            lines.append(f'  `{name}` LONGTEXT,')
        elif ctype == 'text':
            lines.append(f'  `{name}` TEXT,')
        elif ctype == 'int':
            lines.append(f'  `{name}` INT,')
        elif ctype == 'datetime':
            lines.append(f'  `{name}` DATETIME,')
        else:
            length = clen or 255
            lines.append(f'  `{name}` VARCHAR({length}) ,')
    # management fields
    lines.append("  `status` ENUM('pending','approved','rejected') DEFAULT 'pending',")
    lines.append('  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,')
    lines.append('  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    lines.append(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='示例数据 Excel 文件路径')
    parser.add_argument('--out', default='scripts/sql/recreate_is_elements.sql', help='输出 SQL 文件路径')
    args = parser.parse_args()

    p = Path(args.excel)
    if not p.exists():
        print('找不到 Excel 文件:', p)
        raise SystemExit(2)

    xls = pd.read_excel(p, sheet_name=None)
    # choose first non-empty sheet
    sheet = None
    for name, df in xls.items():
        if df.shape[1] > 0:
            sheet = df
            sheet_name = name
            break
    if sheet is None:
        print('未找到含列的 sheet')
        raise SystemExit(3)

    # infer columns
    seen = {}
    col_defs = {}
    for col in sheet.columns:
        cname = normalize_col(col)
        # avoid duplicates
        if cname in seen:
            i = 2
            while f'{cname}_{i}' in seen:
                i += 1
            cname = f'{cname}_{i}'
        seen[cname] = col
        ctype, clen = infer_type(sheet[col])
        col_defs[cname] = (ctype, clen)

    # preserve management and submitter fields from original model/schema if not present in Excel
    preserved = {
        'comment': ('longtext', None),
        'submitter_first_name': ('varchar', 50),
        'submitter_last_name': ('varchar', 50),
        'submitter_institution': ('varchar', 200),
        'submitter_department': ('varchar', 200),
        'submitter_postal_address': ('varchar', 300),
        'submitter_postal_code': ('varchar', 20),
        'submitter_country': ('varchar', 100),
        'submitter_email': ('varchar', 200),
        'submitter_telephone': ('varchar', 50),
        'submitter_id': ('int', None),
        'reviewer_id': ('int', None),
        'submission_date': ('datetime', None),
        'review_date': ('datetime', None),
        'review_comment': ('longtext', None),
    }
    for k, v in preserved.items():
        if k not in col_defs:
            col_defs[k] = v

    # ensure output dir
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    rename_sql = f"RENAME TABLE `is_elements` TO `is_elements_backup_{timestamp}`; -- backup old table if exists\n"
    create_sql = build_table_sql(col_defs, table_name='is_elements')

    out_sql = rename_sql + '\n' + create_sql + '\n'
    outp.write_text(out_sql, encoding='utf-8')

    print('已生成 SQL 文件:', outp)
    print('\n摘要:')
    print('  sheet:', sheet_name, 'shape=', sheet.shape)
    print('  列数:', len(col_defs))
    print('\n前 20 列样例及类型:')
    cnt = 0
    for k, v in list(col_defs.items())[:20]:
        print(f'  {k:30} -> {v[0]}{("("+str(v[1])+")") if v[1] else ""}')
    print('\n注意：生成的 SQL 仅为建议。请在备份数据库并确认无误后手工执行该 SQL 来覆盖原表。')


if __name__ == '__main__':
    main()
