#!/usr/bin/env python3
import logging
import os
import sys
import threading
from pathlib import Path

# === 1. SETUP LOGGING FIRST ===
PROJECT_DIR = Path(__file__).parent
LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

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

# === 2. IMPORT APP & START SENSORS ===
try:
    from dashboard.app import app, log_readings_loop
    
    # Start sensor logging thread
    sensor_thread = threading.Thread(target=log_readings_loop, daemon=True, name='SensorThread')
    sensor_thread.start()
    logger.info("Sensor logging thread started")
    
    # === 3. DATABASE SETUP ===
    with app.app_context():
        from models import db
        db.create_all()
        logger.info("Database tables created")
    
    # === 4. START FLASK SERVER ===
    logger.info("Starting Flask server on 0.0.0.0:5000")
    
    # Production WSGI server
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=False)
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Service startup failed: {e}")
    sys.exit(1)