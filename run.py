#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proISDB Flask application entry point.
"""
import os
import click
from flask import current_app
from flask.cli import with_appcontext
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import User, ISElement, KnowledgeCategory, SystemConfig

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Shell context."""
    return {
        'db': db,
        'User': User,
        'ISElement': ISElement,
        'KnowledgeCategory': KnowledgeCategory,
        'SystemConfig': SystemConfig
    }

@app.cli.command()
@click.option('--username', prompt=True, help='Root username')
@click.option('--email', prompt=True, help='Root email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Root password')
def create_root(username, email, password):
    """Create root super-admin user."""
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo(f'User {username} already exists.')
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

    click.echo(f'Root user {username} created successfully.')
    click.echo('Note: Root user has full privileges. Keep credentials safe.')

@app.cli.command()
@with_appcontext
def init_db():
    """Initialize database with defaults."""
    db.create_all()

    configs = [
        ('site_name', 'proISDB', 'Site name'),
        ('site_description', 'IS element database platform', 'Site description'),
        ('records_per_page', '20', 'Records per page'),
        ('enable_registration', 'true', 'Enable user registration'),
        ('require_approval', 'true', 'Require approval for submissions'),
        ('max_file_size', '16777216', 'Max file upload size (bytes)')
    ]

    for key, value, desc in configs:
        if not SystemConfig.query.filter_by(config_key=key).first():
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=desc
            )
            db.session.add(config)

    categories = [
        ('IS Elements Basics', 'Basic concepts and classification of IS elements'),
        ('Transposition Mechanisms', 'Transposition mechanisms and regulation'),
        ('Evolutionary Analysis', 'Role of IS elements in genome evolution'),
        ('Experimental Methods', 'Experimental techniques for IS element research')
    ]

    for name, desc in categories:
        if not KnowledgeCategory.query.filter_by(name=name).first():
            category = KnowledgeCategory(name=name, description=desc)
            db.session.add(category)

    db.session.commit()
    click.echo('Database initialized.')

@app.cli.command()
@click.option('--drop', is_flag=True, help='Drop all tables before recreating')
def reset_db(drop):
    """Reset database."""
    if drop:
        db.drop_all()
        click.echo('All tables dropped.')

    db.create_all()
    click.echo('Database reset complete.')

@app.cli.command()
def test():
    """Run tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5500))
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', 'on', '1']
    app.run(host='127.0.0.1', port=port, debug=debug_mode)
