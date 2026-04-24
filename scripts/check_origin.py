#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 is_elements 表中 origin 字段是否有数据的脚本
"""
import sys
import os
from sqlalchemy import create_engine, text

# ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import Config

def main():
    uri = Config.SQLALCHEMY_DATABASE_URI
    print(f'Using DB URI: {uri}')
    engine = create_engine(uri)
    with engine.connect() as conn:
        # count non-null, non-empty origin
        q_count = text("SELECT COUNT(*) AS cnt FROM is_elements WHERE origin IS NOT NULL AND TRIM(origin) != ''")
        r = conn.execute(q_count).fetchone()
        if r is None:
            cnt = 0
        else:
            try:
                # try mapping-style access
                cnt = r['cnt']
            except Exception:
                # fallback to positional
                cnt = r[0]
        print(f"is_elements with non-empty origin: {cnt}")

        # show sample rows
        q_sample = text("SELECT id, name, origin FROM is_elements WHERE origin IS NOT NULL AND TRIM(origin) != '' LIMIT 5")
        samples = conn.execute(q_sample).fetchall()
        if samples:
            print('\nSample rows (id, name, origin):')
            for row in samples:
                # row may be Row object
                try:
                    print(f"{row['id']}	{row['name']}	{row['origin']}")
                except Exception:
                    print('\t'.join(str(x) for x in row))
        else:
            print('No non-empty origin values found.')

if __name__ == '__main__':
    main()
