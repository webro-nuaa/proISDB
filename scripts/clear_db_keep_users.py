#!/usr/bin/env python3
"""
清空当前数据库中除用户账号表外的所有数据，并应用重新创建 `is_elements` 的 SQL。

用法:
  # 先做备份（可选）并执行清理+重建（--yes 表示确认执行）
  python scripts/clear_db_keep_users.py --sql scripts/sql/recreate_is_elements.sql --yes --backup

说明:
 - 默认会使用 `config.Config.SQLALCHEMY_DATABASE_URI` 中的连接信息，或可通过 --db-uri 覆盖。
 - 脚本默认保留 `users` 表（可通过 --preserve 指定额外要保留的表，逗号分隔）。
 - 出于安全，必须提供 --yes 才会执行破坏性操作。
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine.url import make_url

try:
    from config.config import Config
    DEFAULT_DB_URI = Config.SQLALCHEMY_DATABASE_URI
except Exception:
    DEFAULT_DB_URI = None


def run_backup(uri, out_path):
    # Try to run mysqldump; parse credentials from uri
    url = make_url(uri)
    user = url.username or ''
    password = url.password or ''
    host = url.host or 'localhost'
    dbname = url.database

    if not dbname:
        raise SystemExit('无法从 URI 中解析数据库名，用 --db-uri 指定正确的 URI')

    cmd = [
        'mysqldump',
        f'--user={user}',
        f'--host={host}',
        '--single-transaction',
        '--quick',
        '--routines',
        '--events',
        dbname
    ]
    if password:
        cmd.insert(1, f'--password={password}')

    print('Running backup:', ' '.join(cmd), '>', out_path)
    with open(out_path, 'wb') as f:
        p = subprocess.Popen(cmd, stdout=f)
        rc = p.wait()
        if rc != 0:
            raise SystemExit(f'mysqldump failed with exit code {rc}')


def execute_sql_file(conn, sql_path):
    sql = Path(sql_path).read_text(encoding='utf-8')
    # split statements by semicolon; naive but works for our generated SQL
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        # execute each statement
        conn.execute(text(stmt))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-uri', default=DEFAULT_DB_URI, help='SQLAlchemy DB URI to use (overrides config)')
    parser.add_argument('--sql', required=True, help='Path to SQL file to apply after cleanup (e.g. scripts/sql/recreate_is_elements.sql)')
    parser.add_argument('--preserve', default='users', help='Comma-separated table names to preserve (default: users)')
    parser.add_argument('--dry-run', action='store_true', help='列出将要被清空的表但不执行任何写操作')
    parser.add_argument('--backup', action='store_true', help='Run mysqldump backup before destructive operations')
    parser.add_argument('--backup-out', default='db_backup_before_clear.sql', help='Backup output path')
    parser.add_argument('--yes', action='store_true', help='Confirm destructive operation')
    args = parser.parse_args()

    if not args.db_uri:
        print('没有可用的数据库 URI；请设置环境或通过 --db-uri 指定。')
        raise SystemExit(2)

    if args.dry_run:
        print('Dry-run 模式：将列出将会被清空的表（不执行写操作）')

    if not args.yes and not args.dry_run:
        print('危险操作：此脚本将清空除保留表之外的所有表数据。请用 --yes 参数确认，或加 --dry-run 先查看受影响表。')
        raise SystemExit(3)

    sql_path = Path(args.sql)
    if not sql_path.exists():
        print('指定的 SQL 文件不存在:', sql_path)
        raise SystemExit(4)

    preserve = [p.strip() for p in args.preserve.split(',') if p.strip()]
    print('Preserve tables:', preserve)

    if args.backup:
        out = Path(args.backup_out)
        print('Backing up database to', out)
        run_backup(args.db_uri, out)
        print('Backup finished.')

    engine = create_engine(args.db_uri)
    with engine.connect() as conn:
        # get all tables
        insp = inspect(engine)
        all_tables = insp.get_table_names()
        print('Found tables:', all_tables)

        to_clear = [t for t in all_tables if t not in preserve]
        print('Tables to clear (truncate):', to_clear)

        if args.dry_run:
            print('Dry-run complete. No changes were made.')
            return

        trans = conn.begin()
        try:
            # disable foreign key checks
            conn.execute(text('SET FOREIGN_KEY_CHECKS=0'))

            for t in to_clear:
                print('Truncating table:', t)
                conn.execute(text(f'TRUNCATE TABLE `{t}`'))

            # apply provided SQL (e.g., rename + create new is_elements)
            print('Applying SQL file:', sql_path)
            execute_sql_file(conn, sql_path)

            conn.execute(text('SET FOREIGN_KEY_CHECKS=1'))
            trans.commit()
            print('Database cleared (except preserved tables) and SQL applied successfully.')
        except Exception as e:
            trans.rollback()
            print('错误，已回滚。错误信息:', e)
            raise


if __name__ == '__main__':
    main()
