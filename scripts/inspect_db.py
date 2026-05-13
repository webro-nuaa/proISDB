#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_db.py

在本地连接项目数据库并打印运行时 schema（表、列、主键、外键、索引、视图）的简单工具。

用法:
  # 使用项目默认配置 (FLASK_CONFIG 环境变量决定配置名称)
  python scripts/inspect_db.py

  # 指定数据库 URI（覆盖配置）
  python scripts/inspect_db.py --db-uri "mysql+pymysql://user:pass@host/dbname?charset=utf8mb4"

输出将打印到 stdout — 适合粘贴到聊天里给我以便我做进一步分析。
"""

import os
import json
import argparse
from pprint import pprint

# 尝试加载 dotenv（若存在）以便从 .env 获取数据库配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv 非必须，忽略错误
    pass

# 尝试从项目配置中获取默认 URI
DB_URI = None
try:
    from config.config import config
    cfg_name = os.getenv('FLASK_CONFIG', 'development')
    Conf = config.get(cfg_name)
    DB_URI = getattr(Conf, 'SQLALCHEMY_DATABASE_URI', None)
    if not DB_URI:
        # fallback: build from MYSQL_* variables on the config class or env vars
        MYSQL_HOST = getattr(Conf, 'MYSQL_HOST', os.getenv('MYSQL_HOST', 'localhost'))
        MYSQL_USER = getattr(Conf, 'MYSQL_USER', os.getenv('MYSQL_USER', 'root'))
        MYSQL_PASSWORD = getattr(Conf, 'MYSQL_PASSWORD', os.getenv('MYSQL_PASSWORD', ''))
        MYSQL_DB = getattr(Conf, 'MYSQL_DB', os.getenv('MYSQL_DB', ''))
        DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'
except Exception:
    DB_URI = None


def inspect_database(uri):
    """使用 SQLAlchemy inspector 检查数据库结构并返回一个 Python dict。"""
    try:
        from sqlalchemy import create_engine, inspect, text
        from sqlalchemy.exc import SQLAlchemyError
    except Exception as e:
        print('缺少依赖：请确保已安装 sqlalchemy 和相应的 DB 驱动（例如 pymysql 或 mysql-connector-python）')
        print('安装示例: pip install SQLAlchemy pymysql')
        raise

    engine = create_engine(uri)
    inspector = inspect(engine)

    result = {}
    try:
        tables = inspector.get_table_names()
        result['tables'] = {}
        for t in tables:
            cols = inspector.get_columns(t)
            pk = inspector.get_pk_constraint(t)
            fks = inspector.get_foreign_keys(t)
            indexes = inspector.get_indexes(t)
            result['tables'][t] = {
                'columns': [{ 'name': c['name'], 'type': str(c['type']), 'nullable': c.get('nullable', True), 'default': c.get('default') } for c in cols],
                'primary_key': pk.get('constrained_columns') if pk else [],
                'foreign_keys': fks,
                'indexes': indexes
            }
        # list views (information_schema)
        try:
            with engine.connect() as conn:
                views = conn.execute(text("SELECT table_name FROM information_schema.views WHERE table_schema = DATABASE();")).fetchall()
                result['views'] = [v[0] for v in views]
        except Exception:
            result['views'] = []

        return result
    except SQLAlchemyError as e:
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inspect runtime database schema for proISDB project')
    parser.add_argument('--db-uri', help='数据库 URI，覆盖项目配置，例如 mysql+pymysql://user:pass@host/dbname?charset=utf8mb4')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出到 stdout 或文件（配合 --output 使用）')
    parser.add_argument('--output', help='将 JSON 输出保存到指定文件路径（会覆盖或创建文件）')
    args = parser.parse_args()

    uri = args.db_uri or DB_URI or os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')

    if not uri:
        print('找不到数据库连接信息。请通过下列任一方式提供：')
        print('  1) 在环境变量中设置 FLASK_CONFIG 指向 config 中的配置，或设置 MYSQL_HOST/ MYSQL_USER/ MYSQL_PASSWORD/ MYSQL_DB')
        print('  2) 使用 --db-uri 参数传入完整的连接 URI')
        exit(2)

    # 尝试隐藏密码片段以免直接打印明文
    masked_uri = uri
    pwd = os.getenv('MYSQL_PASSWORD')
    if pwd and pwd in uri:
        masked_uri = uri.replace(pwd, '***')
    # 进一步尝试按协议://user:pass@host 做简单遮掩（若存在）
    try:
        import re
        masked_uri = re.sub(r'(//[^:]+):([^@]+)@', r"\1:***@", masked_uri)
    except Exception:
        pass
    print('使用数据库 URI (部分隐藏):', masked_uri)

    try:
        schema = inspect_database(uri)
    except Exception as e:
        print('检查数据库时出错:', e)
        raise

    if args.json or args.output:
        # 将 schema 写为 JSON（优先写入文件，如果未提供文件则写入 stdout）
        out_json = json.dumps(schema, ensure_ascii=False, indent=2)
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(out_json)
                print(f'✓ 已将 JSON schema 写入: {args.output}')
            except Exception as e:
                print(f'✗ 写入文件 {args.output} 失败: {e}')
                print('\n将 JSON 打印到 stdout:')
                print(out_json)
        else:
            print(out_json)
    else:
        # 打印可读摘要，再输出完整 JSON
        print('\nSummary: {} tables, {} views'.format(len(schema.get('tables', {})), len(schema.get('views', []))))
        for t, meta in schema.get('tables', {}).items():
            print('\nTable:', t)
            print('  Columns:')
            for c in meta['columns']:
                print("    - {name} ({type}) nullable={nullable} default={default}".format(**c))
            print('  PK:', meta.get('primary_key'))
            if meta.get('foreign_keys'):
                print('  FKs:')
                for fk in meta.get('foreign_keys'):
                    print('    -', fk)
            if meta.get('indexes'):
                print('  Indexes:')
                for idx in meta.get('indexes'):
                    print('    -', idx)

        print('\nFull schema JSON (for programmatic use):')
        pprint(schema)
