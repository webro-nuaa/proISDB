#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proISDB Flask应用启动文件
"""
import os
import click
from flask import current_app
from flask.cli import with_appcontext
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

from app import create_app, db
from app.models import User, ISElement, KnowledgeCategory, SystemConfig

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Shell上下文"""
    return {
        'db': db,
        'User': User,
        'ISElement': ISElement,
        'KnowledgeCategory': KnowledgeCategory,
        'SystemConfig': SystemConfig
    }

@app.cli.command()
@click.option('--username', prompt=True, help='ROOT用户名')
@click.option('--email', prompt=True, help='ROOT邮箱')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='ROOT密码')
def create_root(username, email, password):
    """创建ROOT超级管理员"""
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo(f'用户 {username} 已存在')
        return
    
    user = User(
        username=username,
        email=email,
        role='root',
        first_name='Root',
        last_name='Admin',
        is_active=True
    )
    user.password = password
    
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'ROOT用户 {username} 创建成功！')
    click.echo('注意：ROOT用户拥有最高权限，请妥善保管账号密码。')

@app.cli.command()
@with_appcontext
def init_db():
    """初始化数据库"""
    db.create_all()
    
    # 创建默认系统配置
    configs = [
        ('site_name', 'proISDB', '网站名称'),
        ('site_description', 'IS元素数据库和科普平台', '网站描述'),
        ('records_per_page', '20', '每页显示记录数'),
        ('enable_registration', 'true', '是否允许用户注册'),
        ('require_approval', 'true', '新提交数据是否需要审核'),
        ('max_file_size', '16777216', '最大文件上传大小（字节）')
    ]
    
    for key, value, desc in configs:
        if not SystemConfig.query.filter_by(config_key=key).first():
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=desc
            )
            db.session.add(config)
    
    # 创建默认知识分类
    categories = [
        ('IS元素基础', 'IS元素的基本概念和分类'),
        ('转座机制', '转座子的转座机制和调控'),
        ('进化分析', 'IS元素在基因组进化中的作用'),
        ('实验方法', 'IS元素研究的实验技术和方法')
    ]
    
    for name, desc in categories:
        if not KnowledgeCategory.query.filter_by(name=name).first():
            category = KnowledgeCategory(name=name, description=desc)
            db.session.add(category)
    
    db.session.commit()
    click.echo('数据库初始化完成！')

@app.cli.command()
@click.option('--drop', is_flag=True, help='删除所有表后重新创建')
def reset_db(drop):
    """重置数据库"""
    if drop:
        db.drop_all()
        click.echo('已删除所有数据表')
    
    db.create_all()
    click.echo('数据库重置完成！')

@app.cli.command()
def test():
    """运行测试"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5500))
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', 'on', '1']
    app.run(host='127.0.0.1', port=port, debug=debug_mode)
