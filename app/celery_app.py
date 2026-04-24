# -*- coding: utf-8 -*-
from celery import Celery
import os


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(
        result_expires=3600,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
