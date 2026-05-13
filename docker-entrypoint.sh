#!/bin/bash
set -e

# Auto-initialize database tables and default configs on every start.
# flask init-db is idempotent — it only creates what's missing.
flask init-db

# Run the container command (gunicorn for web, celery for worker)
exec "$@"
