#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# Direct paths - no Flask imports needed
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'smart_allotment.db')

print("Running migration: Add last_notified column to alerts...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE alerts ADD COLUMN last_notified DATETIME")
    print("✅ Added last_notified column")
except Exception as e:
    print(f"ℹ️ Column already exists: {e}")

conn.commit()
conn.close()
print("✅ Migration 001 complete!")
