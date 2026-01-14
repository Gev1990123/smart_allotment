#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.app import app, db
from datetime import datetime

print("Running migration: Add last_notified column to alerts...")

with app.app_context():
    try:
        db.engine.execute("ALTER TABLE alerts ADD COLUMN last_notified DATETIME")
        print("Added last_notified column")
    except Exception as e:
        print(f"Column already exists: {e}")
    
    db.create_all()
    print("Migration 001 complete!")
