#!/usr/bin/env bash
set -e

echo "======================================"
echo " Smart Allotment Deployment Started"
echo " $(date)"
echo "======================================"

# ---- CONFIG ----
PROJECT_DIR="/home/pi/smart_allotment"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/deploy.log"
MAIN_SCRIPT="main.py"

# ---- ENSURE DIRECTORIES EXIST ----
mkdir -p "$LOG_DIR"

# ---- LOG EVERYTHING ----
exec >> "$LOG_FILE" 2>&1

echo "Changing to project directory"
cd "$PROJECT_DIR"

# ---- SET UP PYTHON VENV ----
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment"
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment"
source "$VENV_DIR/bin/activate"

# ---- INSTALL DEPENDENCIES ----
echo "Upgrading pip"
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies"
  pip install -r requirements.txt
else
  echo "No requirements.txt found — skipping"
fi

# ---- OPTIONAL: STOP PREVIOUS INSTANCE ----
if pgrep -f "$MAIN_SCRIPT" > /dev/null; then
  echo "Stopping existing $MAIN_SCRIPT"
  pkill -f "$MAIN_SCRIPT"
fi

# ---- START APPLICATION ----
if [ -f "$MAIN_SCRIPT" ]; then
  echo "Starting $MAIN_SCRIPT"
  nohup python "$MAIN_SCRIPT" >> "$LOG_DIR/app.log" 2>&1 &
  echo "$MAIN_SCRIPT started successfully"
else
  echo "ERROR: $MAIN_SCRIPT not found!"
  exit 1
fi

echo "======================================"
echo " Deployment completed successfully"
echo "======================================"
