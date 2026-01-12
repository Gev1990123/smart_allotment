#!/usr/bin/env python3
import logging
import os
import sys
import threading
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# === 1. SETUP EVERYTHING BEFORE IMPORTING APP ===
PROJECT_DIR = Path(__file__).parent
LOG_DIR = PROJECT_DIR / "logs"
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("=== Smart Allotment service starting ===")

# Create Flask app & DB FIRST
app = Flask(__name__)
BASE_DIR = str(PROJECT_DIR)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'smart_allotment.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logger.info("Flask app and database initialized")

# === 2. NOW SAFE TO IMPORT APP ===
from dashboard.app import log_readings_loop, index, get_alerts, readings
logger.info("Dashboard module imported")

# === 3. REGISTER ROUTES ===
app.add_url_rule('/', view_func=index)
app.add_url_rule('/alerts', view_func=get_alerts)
app.add_url_rule('/api/readings', view_func=readings)
logger.info("Routes registered")

# === 4. START SENSOR THREAD (ONLY ONCE, with app & db) ===
sensor_thread = threading.Thread(target=lambda: log_readings_loop(app, db), daemon=True, name='SensorThread')
sensor_thread.start()
logger.info("Sensor logging thread started")

# === 5. CREATE TABLES ===
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

# === 6. START SERVER ===
logger.info("Starting Flask server on 0.0.0.0:5000")
from werkzeug.serving import run_simple
run_simple('0.0.0.0', 5000, app, use_reloader=False)