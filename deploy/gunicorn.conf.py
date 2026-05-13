import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5500')}"
workers = int(os.environ.get('GUNICORN_WORKERS', '4'))
worker_class = "gthread"
threads = int(os.environ.get('GUNICORN_THREADS', '2'))
timeout = 120
keepalive = 5
preload_app = os.environ.get('GUNICORN_PRELOAD_APP', 'true').lower() in ['true', 'on', '1']
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
max_requests = 1000
max_requests_jitter = 50
