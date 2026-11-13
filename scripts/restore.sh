
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv-backup/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Backup virtual environment not found: $VENV_PYTHON" >&2
  exit 1
fi

cd "$PROJECT_DIR"

exec "$VENV_PYTHON" scripts/backup_manager.py restore "$@"
