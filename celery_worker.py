# -*- coding: utf-8 -*-
import os
from app.celery_app import make_celery
from app import create_app

flask_app = create_app(os.getenv('FLASK_ENV', 'development') or 'development')
celery = make_celery(flask_app)
