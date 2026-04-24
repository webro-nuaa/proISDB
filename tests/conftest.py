# -*- coding: utf-8 -*-
import os
import pytest
from app import create_app, db as _db
from app.models import User, ISElement, KnowledgeCategory, SystemConfig


os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('MYSQL_PASSWORD', 'test_password')


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app.config['SERVER_NAME'] = 'localhost'
    yield app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()


@pytest.fixture(scope='function')
def test_user(db):
    user = User(
        username='testuser',
        email='test@example.com',
        role='visitor',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    user.password = 'TestPass123'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    user = User(
        username='adminuser',
        email='admin@example.com',
        role='admin',
        first_name='Admin',
        last_name='User',
        is_active=True
    )
    user.password = 'AdminPass123'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def root_user(db):
    user = User(
        username='rootuser',
        email='root@example.com',
        role='root',
        first_name='Root',
        last_name='Admin',
        is_active=True
    )
    user.password = 'RootPass123'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def logged_in_client(client, test_user):
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    return client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    client.post('/auth/login', data={
        'username': 'adminuser',
        'password': 'AdminPass123'
    })
    return client


@pytest.fixture(scope='function')
def sample_elements(db):
    elements = []
    data = [
        {'name': 'IS1', 'family': 'IS1', 'group': 'IS1', 'host': 'Escherichia coli', 'status': 'approved', 'is_length': 768, 'origin': 'plasmid'},
        {'name': 'IS2', 'family': 'IS3', 'group': 'IS3', 'host': 'Salmonella enterica', 'status': 'approved', 'is_length': 1200, 'origin': 'chromosome'},
        {'name': 'IS3', 'family': 'IS3', 'group': 'IS3', 'host': 'Escherichia coli', 'status': 'approved', 'is_length': 1300, 'origin': 'plasmid'},
        {'name': 'IS4', 'family': 'IS5', 'group': 'IS4', 'host': 'Bacillus subtilis', 'status': 'approved', 'is_length': 1400, 'origin': 'chromosome'},
        {'name': 'IS5-pending', 'family': 'IS1', 'group': 'IS1', 'host': 'Pseudomonas', 'status': 'pending', 'is_length': 800, 'origin': 'plasmid'},
    ]
    for d in data:
        el = ISElement(**d)
        db.session.add(el)
        elements.append(el)
    db.session.commit()
    return elements


@pytest.fixture(scope='function')
def system_configs(db):
    configs = [
        SystemConfig(config_key='site_name', config_value='proISDB', description='Site name'),
        SystemConfig(config_key='enable_registration', config_value='true', config_type='boolean'),
    ]
    for c in configs:
        db.session.add(c)
    db.session.commit()
    return configs
