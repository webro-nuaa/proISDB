#!/bin/bash
# proISDB 数据库自动备份脚本
# 用法: ./scripts/backup.sh [--upload]
# --upload: 备份后上传到远程存储（需配置 rclone）

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/opt/proisdb/backups}"
KEEP_DAYS="${KEEP_DAYS:-30}"
MYSQL_CONTAINER="${MYSQL_CONTAINER:-proisdb-mysql-1}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_DB="${MYSQL_DB:-proisdb_db}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/proisdb_db_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "=== proISDB Backup Started: $(date) ==="

echo "[1/3] Dumping MySQL database..."
if [ -n "${MYSQL_PASSWORD}" ]; then
    sudo docker exec "${MYSQL_CONTAINER}" mysqldump -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
        --single-transaction --routines --triggers "${MYSQL_DB}" 2>/dev/null | gzip > "${BACKUP_FILE}"
else
    sudo docker exec "${MYSQL_CONTAINER}" mysqldump -u"${MYSQL_USER}" \
        --single-transaction --routines --triggers "${MYSQL_DB}" 2>/dev/null | gzip > "${BACKUP_FILE}"
fi

if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "  -> Backup created: ${BACKUP_FILE} (${SIZE})"
else
    echo "  -> ERROR: Backup file not created!"
    exit 1
fi

echo "[2/3] Cleaning up backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "proisdb_db_*.sql.gz" -mtime +${KEEP_DAYS} -delete 2>/dev/null || true
echo "  -> Done"

if [ "${1:-}" = "--upload" ] && command -v rclone &>/dev/null; then
    echo "[3/3] Uploading to remote storage..."
    rclone copy "${BACKUP_FILE}" remote:proisdb-backups/ 2>/dev/null && echo "  -> Uploaded" || echo "  -> Upload failed"
else
    echo "[3/3] Upload skipped (use --upload or install rclone)"
fi

echo "=== Backup Completed: $(date) ==="
