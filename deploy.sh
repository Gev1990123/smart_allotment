#!/usr/bin/env bash
set -e

PROJECT_DIR="/home/smartallotment/smart_allotment"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/deploy.log"
SERVICE="smart-allotment"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

cd "$PROJECT_DIR"

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  log_info "Update detected ($(git rev-parse --short origin/main))"

  git reset --hard origin/main
  log_info "✓ Reset to $(git rev-parse --short HEAD)"

  source "$VENV_DIR/bin/activate"
  # Capture pip output, only log changes/errors
  UPDATED=$(pip install -r requirements.txt 2>&1 | grep -E "(Successfully installed|Requirement already satisfied)" | wc -l)
  if [ $? -eq 0 ]; then
      log_success "✓ Pip install complete ($UPDATED packages processed)"
  else
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] Pip install failed" >&2
      exit 1
  fi

  sudo systemctl restart $SERVICE
  log_success "✓ Service '$SERVICE' restarted"
else
  log_info "No update needed"
fi

log_success "Deploy complete"