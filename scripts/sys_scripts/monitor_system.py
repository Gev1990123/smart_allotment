#!/usr/bin/env python3
import os
import psutil
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.notifications import send_email_alert
import logging
from utils.logger import setup

## Setup Logging
setup("system_monitor.log")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'smart_allotment.db')

# Get stats
cpu = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory().percent
db_size_mb = os.path.getsize(DB_PATH) / (1024*1024)

logging.info(f"CPU: {cpu}% | MEM: {mem}% | DB: {db_size_mb:.1f}MB")

# Alert if critical (no cooldown - urgent!)
if cpu > 80:
    subject = f"High CPU: {cpu}%"
    body = f"Allotment system CPU usage is critically high: {cpu}%. Check server immediately."
    admin = True

    send_email_alert(subject=subject, body=body, to_email=None, admin=admin)
    logging.warning(f"Email sent to Administrator - High CPU: {cpu}%")

if mem > 80:
    subject = f"High Memory: {mem}%"
    body = f"Allotment system memory usage is critically high: {mem}%. Check server immediately."
    admin = True

    send_email_alert(subject=subject, body=body, to_email=None, admin=admin)
    logging.warning(f"Email sent to Administrator - High Memory: {mem}%")

if db_size_mb > 50:
    subject = f"Database Large: {db_size_mb:.1f}MB"
    body = f"Allotment database has grown to {db_size_mb:.1f}MB. Run cleanup recommended."
    admin = True

    send_email_alert(subject=subject, body=body, to_email=None, admin=admin)
    logging.warning(f"Email sent to Administrator - Database Large: {db_size_mb:.1f}MB")