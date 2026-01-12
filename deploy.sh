#!/usr/bin/env bash
set -e

PROJECT_DIR="/home/smartallotment/smart_allotment"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/data/logs"
LOG_FILE="$LOG_DIR/data/deploy.log"
SERVICE="smart-allotment"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

cd "$PROJECT_DIR"

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "Update detected: $(date)"

  git reset --hard origin/main

  source "$VENV_DIR/bin/activate"
  pip install -r requirements.txt

  sudo systemctl restart $SERVICE
else
  echo "No update: $(date)"
fi