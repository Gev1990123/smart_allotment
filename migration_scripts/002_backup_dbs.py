#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
from datetime import datetime
from dashboard.app import app

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'smart_allotment.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"smart_allotment_{timestamp}.db")
    
    # SQLite safe backup using app context
    with app.app_context():
        shutil.copy2(DB_PATH, backup_file)
    
    print(f"✅ Backup created: {backup_file}")
    print(f"📁 All backups: {BACKUP_DIR}")

if __name__ == "__main__":
    backup_database()
