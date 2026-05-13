#!/bin/bash
# proISDB 部署脚本
# 用法:
#   ./scripts/deploy.sh          - 完整部署（构建+启动）
#   ./scripts/deploy.sh update   - 滚动更新（仅重启 web 和 celery_worker）
#   ./scripts/deploy.sh stop     - 停止所有服务
#   ./scripts/deploy.sh status   - 查看服务状态
#   ./scripts/deploy.sh logs     - 查看实时日志

set -euo pipefail

COMPOSE_FILE="docker-compose.yml"
COMPOSE_CMD="sudo docker compose"

cd "$(dirname "$0")/.."

check_env() {
    if [ ! -f .env ]; then
        echo "ERROR: .env file not found! Copy .env.example and configure it."
        echo "  cp .env.example .env"
        exit 1
    fi
}

deploy_full() {
    echo "=== Full Deploy Started ==="
    check_env

    echo "[1/5] Building Docker images..."
    $COMPOSE_CMD -f $COMPOSE_FILE build

    echo "[2/5] Starting all services..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d

    echo "[3/5] Waiting for services to be healthy..."
    sleep 15

    echo "[4/5] Checking health..."
    HEALTH=$($COMPOSE_CMD -f $COMPOSE_FILE exec web python -c \
        "import urllib.request; r=urllib.request.urlopen('http://localhost:5500/health'); print(r.read().decode())" 2>/dev/null || echo "FAILED")
    echo "  Health: $HEALTH"

    echo "[5/5] Running database migrations..."
    $COMPOSE_CMD -f $COMPOSE_FILE exec web flask db upgrade 2>/dev/null || echo "  No pending migrations"

    echo "=== Deploy Completed ==="
    $COMPOSE_CMD -f $COMPOSE_FILE ps
}

deploy_update() {
    echo "=== Rolling Update Started ==="
    check_env

    echo "[1/4] Building new images..."
    $COMPOSE_CMD -f $COMPOSE_FILE build web celery_worker

    echo "[2/4] Updating web service (zero-downtime)..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d --no-deps --build web

    echo "[3/4] Waiting for web health check..."
    sleep 10
    for i in $(seq 1 6); do
        if curl -sf http://localhost:5500/health > /dev/null 2>&1; then
            echo "  -> Web is healthy"
            break
        fi
        if [ $i -eq 6 ]; then
            echo "  -> ERROR: Web health check failed after 60s!"
            echo "  -> Rolling back..."
            $COMPOSE_CMD -f $COMPOSE_FILE restart web
            exit 1
        fi
        echo "  -> Waiting... ($i/6)"
        sleep 10
    done

    echo "[4/4] Updating celery worker..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d --no-deps --build celery_worker

    echo "=== Update Completed ==="
    $COMPOSE_CMD -f $COMPOSE_FILE ps
}

deploy_stop() {
    echo "=== Stopping All Services ==="
    $COMPOSE_CMD -f $COMPOSE_FILE down
    echo "=== Stopped ==="
}

deploy_status() {
    echo "=== Service Status ==="
    $COMPOSE_CMD -f $COMPOSE_FILE ps
    echo ""
    echo "=== Health Check ==="
    curl -sf http://localhost:5500/health 2>/dev/null && echo "" || echo "  Web: UNREACHABLE"
}

deploy_logs() {
    $COMPOSE_CMD -f $COMPOSE_FILE logs -f --tail=100
}

case "${1:-}" in
    update)  deploy_update ;;
    stop)    deploy_stop ;;
    status)  deploy_status ;;
    logs)    deploy_logs ;;
    *)       deploy_full ;;
esac
