#!/usr/bin/env bash
set -e

echo "======================================"
echo " Smart Allotment Auto Update"
echo " $(date)"
echo "======================================"

# ---- CONFIG ----
PROJECT_DIR="/home/smart-allotment/smart_allotment"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/deploy.log"

DASHBOARD_SERVICE="smart_allotment_dashboard"
LOGGER_SERVICE="smart_allotment_logger"

# ---- ENSURE DIRECTORIES ----
mkdir -p "$LOG_DIR"

# ---- LOG EVERYTHING ----
exec >> "$LOG_FILE" 2>&1

cd "$PROJECT_DIR"

echo "Fetching latest code from GitHub"
git fetch origin main

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
  echo "No updates available. Exiting."
  exit 0
fi

echo "Updates found. Pulling..."
git pull origin main

# ---- PYTHON ENV ----
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Upgrading pip"
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  echo "Installing requirements"
  pip install -r requirements.txt
fi

# ---- DATABASE SAFETY ----
echo "Ensuring data directory exists"
mkdir -p "$PROJECT_DIR/data"

# ---- RESTART SERVICES ----
echo "Restarting services"
sudo systemctl restart "$LOGGER_SERVICE"
sudo systemctl restart "$DASHBOARD_SERVICE"

echo "======================================"
echo " Update complete"
echo "======================================"