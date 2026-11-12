#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="/etc/trabalho-web-iii-backup.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi
cd "$PROJECT_DIR"
exec python3 scripts/backup_manager.py create --project-dir "$PROJECT_DIR"
