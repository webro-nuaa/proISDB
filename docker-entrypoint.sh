#!/bin/bash
set -e

# Auto-initialize database tables and default configs on every start.
# flask init-db is idempotent — it only creates what's missing.
flask init-db

# Auto-create root user if ROOT_USERNAME/ROOT_EMAIL/ROOT_PASSWORD are set in .env
flask create-root --auto-create

# Run the container command (gunicorn for web, celery for worker)
exec "$@"
