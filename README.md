# InsertQ (proISDB)

Insertion Sequence (IS) element database platform with BLAST alignment, advanced search, and community-driven data submission.

## Features

- **IS Element Search** — Simple and advanced search with multi-field filtering
- **BLAST Alignment** — Local blastn/blastp sequence alignment via NCBI BLAST+
- **Knowledge Base** — Community articles with Markdown support
- **Data Submission** — User-submitted IS element data with admin review workflow
- **Admin Dashboard** — User management, data review, batch import, statistics
- **REST API** — Swagger-documented API endpoints
- **Email Verification** — Secure email change workflow
- **Download Request** — Visitor data download application system

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 2.3.3, SQLAlchemy, Celery 5.3 |
| Database | MySQL 8.4, Redis 7 |
| Search | SQLAlchemy ORM (LIKE query) |
| BLAST | NCBI BLAST+ (local) |
| WSGI | Gunicorn (gthread) |
| Reverse Proxy | Nginx (HTTPS) |
| Deployment | Docker Compose |
| CI/CD | GitHub Actions |
| Error Tracking | Sentry (optional) |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Deploy

```bash
# Clone the repository
git clone https://github.com/webro-nuaa/InsertQ.git
cd InsertQ

# Configure environment
cp .env.example .env
nano .env

# Build and start all services
sudo docker compose build
sudo docker compose up -d
```

### Configure .env

Only **2 values** must be changed:

```
# Generate a random secret key:
python -c "import secrets; print(secrets.token_hex(32))"

MYSQL_PASSWORD=your-strong-password    # MySQL root password
SECRET_KEY=generated-random-string     # Flask encryption key
```

All other values are automatically overridden by `docker-compose.yml`.

### Verify

```bash
curl http://localhost:5500/health
```

## Architecture

```
Internet
  └── Nginx (:80/:443, HTTPS)
        └── Flask/Gunicorn (127.0.0.1:5500, internal only)
              ├── MySQL 8.4 (internal, no exposed port)
              ├── Redis 7 (internal, no exposed port)
              │     ├── DB 0: Celery broker
              │     ├── DB 1: Cache
              │     └── DB 2: Session
              └── Celery Worker (BLAST tasks)
```

## Services

| Service | Port | Exposed | Description |
|---------|------|---------|-------------|
| web | 5500 | localhost only | Flask application |
| celery_worker | — | no | Async task processor (BLAST) |
| mysql | 3306 | no | Database (internal) |
| redis | 6379 | no | Cache, session, broker (internal) |

## Development

```bash
# Start development environment (code mounted, auto-reload)
sudo docker compose -f docker-compose.dev.yml up -d
```

Changes to templates and Python files are reflected immediately.

## Update

```bash
git pull
sudo docker compose build
sudo docker compose up -d --no-deps web celery_worker
```

## Backup

```bash
./scripts/backup.sh
```

## Migration to New Server

```bash
# On old server: export database
sudo docker exec insertq-mysql-1 mysqldump -u root -p insertq_db > backup.sql

# On new server: clone and deploy
git clone https://github.com/webro-nuaa/InsertQ.git
cd InsertQ
cp .env.example .env && nano .env
sudo docker compose build
sudo docker compose up -d mysql redis
sleep 10
sudo docker exec -i insertq-mysql-1 mysql -u root -p insertq_db < backup.sql
sudo docker compose up -d
```

## Testing

```bash
sudo docker exec insertq-web-1 python -m pytest tests/ -v
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
tests/                   # pytest test suite
```

## License

MIT
