# proISDB

Insertion Sequence (IS) element database platform with BLAST alignment, advanced search, and community-driven data submission.

## Features

- **IS Element Search** — Simple and advanced search with multi-field filtering
- **BLAST Alignment** — Local blastn/blastp sequence alignment via NCBI BLAST+
- **Knowledge Base** — Community articles with Markdown support
- **Data Submission** — User-submitted IS element data with admin review workflow
- **Admin Dashboard** — User management, data review, batch import/export, statistics
- **REST API** — Flask-RESTX documented API endpoints
- **Email Verification** — Secure email change workflow
- **Download Request** — Visitor data download application system with admin approval

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 2.3.3, SQLAlchemy, Celery 5.3 |
| Database | MySQL 8.4, Redis 7 |
| Search | SQLAlchemy ORM |
| BLAST | NCBI BLAST+ (local) |
| WSGI | Gunicorn (gthread) |
| Reverse Proxy | Nginx (host-level, HTTPS) |
| Deployment | Docker Compose (4 services) |
| CI/CD | GitHub Actions |
| Error Tracking | Sentry (optional) |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Python 3.11+ (for running CLI commands like `flask create-root`)

### Deploy

```bash
# Clone the repository
git clone https://github.com/webro-nuaa/proISDB.git
cd proISDB

# Configure environment
cp .env.example .env
nano .env

# Build and start all services
sudo docker compose build
sudo docker compose up -d

# Verify
curl http://localhost/health
```

Database init and root admin creation happen automatically on first start (via .env values). Access at `http://your-server-ip` (or `http://localhost` locally).

> For HTTPS, set up a reverse proxy (Nginx). See `deploy/nginx.conf` for a reference config.

### Configure .env

Only **5 values** must be changed for a Docker deployment. Fill them in and the root admin user is created automatically.

```
MYSQL_PASSWORD=your-strong-password       # MySQL root password
SECRET_KEY=generated-random-string        # Flask encryption key
ROOT_USERNAME=root                        # Root admin username
ROOT_EMAIL=admin@example.com              # Root admin email
ROOT_PASSWORD=your-root-password          # Root admin password
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### First-time Setup

No manual steps needed — database tables, default configs, and the root admin user are all created automatically on first container start (driven by your `.env` values).

## Architecture

```
Internet
  └── Flask/Gunicorn (:80) — Docker
        ├── MySQL 8.4 (internal) — Docker
        ├── Redis 7 (internal) — Docker
        │     ├── DB 0: Celery broker
        │     ├── DB 1: Cache
        │     └── DB 2: Session
        └── Celery Worker (BLAST tasks) — Docker

  Optional: Nginx (:443, HTTPS) in front for SSL termination
```

## Services

| Service | Host Port | Purpose |
|---------|-----------|---------|
| web | 80 | Flask application (Gunicorn) |
| celery_worker | — | Async BLAST task processor |
| mysql | — (internal) | Database |
| redis | — (internal) | Cache, session store, Celery broker |

## Development

```bash
# Start dev environment with code hot-reload
sudo docker compose -f docker-compose.dev.yml up -d
```

The dev compose file:
- Mounts `app/` and `config/` directories into the container for live reload
- Exposes MySQL on `127.0.0.1:3307` and Redis on `127.0.0.1:6380` for local tools
- Disables Gunicorn preload so code changes take effect immediately

## Nginx Setup (Optional HTTPS)

For production HTTPS, a reference Nginx config is at `deploy/nginx.conf`. It terminates SSL and proxies to `127.0.0.1:5500` (change to port 80 if running behind Nginx).

```bash
# Install and configure
sudo apt install nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/proisdb
sudo ln -s /etc/nginx/sites-available/proisdb /etc/nginx/sites-enabled/
# Edit server_name and SSL cert paths, then:
sudo nginx -t && sudo systemctl reload nginx
```

For Let's Encrypt SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Update

```bash
# Using the deploy script (recommended)
./scripts/deploy.sh update

# Or manually:
git pull
sudo docker compose build web celery_worker
sudo docker compose up -d --no-deps web celery_worker
```

The `update` command does a rolling restart — web is replaced first, health-checked, then the worker is replaced.

## Backup

```bash
# Local backup (keeps 30 days)
./scripts/backup.sh

# Backup and upload to remote (requires rclone configured)
./scripts/backup.sh --upload
```

Backups are stored in `/opt/proisdb/backups/` by default. Configure `BACKUP_DIR` and `KEEP_DAYS` in the script.

## Migration to New Server

```bash
# On old server: export database
sudo docker exec proISDB-mysql-1 mysqldump -u root -p proisdb_db > backup.sql

# On new server: clone and deploy
git clone https://github.com/webro-nuaa/proISDB.git
cd proISDB
cp .env.example .env && nano .env
sudo docker compose build
sudo docker compose up -d mysql redis
sleep 10
sudo docker exec -i proISDB-mysql-1 mysql -u root -p proisdb_db < backup.sql
sudo docker compose up -d
```

## CLI Commands

```bash
# Manage the app
sudo docker compose exec web flask create-root     # Create root admin (manual override)
sudo docker compose exec web flask reset-db         # Recreate all tables (--drop to wipe first)
sudo docker compose exec web flask test             # Run test suite
```

## Testing

```bash
# In the container
sudo docker compose exec web python -m pytest tests/ -v

# Or locally (needs Python 3.11+ and requirements.txt installed)
python -m pytest tests/ -v
```

## Project Structure

```
app/
├── __init__.py          # Application factory
├── celery_app.py        # Celery configuration
├── forms/               # WTForms form classes
├── models/              # SQLAlchemy models
├── views/               # Flask Blueprint views
│   ├── main.py          # Home, about, health
│   ├── auth.py          # Login, register, profile
│   ├── search.py        # IS element search
│   ├── blast.py         # BLAST alignment
│   ├── knowledge.py     # Knowledge base
│   ├── submission.py    # Data submission
│   ├── admin.py         # Admin dashboard
│   └── api.py           # REST API
├── utils/               # Helpers (BLAST, email, markdown)
├── static/              # CSS, JS, uploads
└── templates/           # Jinja2 HTML templates
blast_db/                # BLAST local databases
config/                  # Environment configurations
deploy/                  # Gunicorn & Nginx configs
scripts/                 # Backup & deploy scripts
tests/                   # pytest test suite (212 tests)
```

## License

MIT
