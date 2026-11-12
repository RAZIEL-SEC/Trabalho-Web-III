
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="/etc/trabalho-web-iii-backup.env"
VENV_PYTHON="$PROJECT_DIR/.venv-backup/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Backup virtual environment not found: $VENV_PYTHON" >&2
  exit 1
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

cd "$PROJECT_DIR"

exec "$VENV_PYTHON" scripts/backup_manager.py create \
  --project-dir "$PROJECT_DIR"
