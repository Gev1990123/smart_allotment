#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# Direct paths - no Flask imports needed
# Calculate project root
current_dir = os.path.abspath(os.path.dirname(__file__))
while os.path.basename(current_dir) != 'smart_allotment':
    parent = os.path.dirname(current_dir)
    if parent == current_dir:
        raise RuntimeError("Could not find smart_allotment project root")
    current_dir = parent

PROJECT_ROOT = current_dir
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'smart_allotment.db')

print("Running migration: Add status column to alerts...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE alerts ADD COLUMN status VARCHAR(20) DEFAULT 'active';")
    print("✅ Added Status column")
except Exception as e:
    print(f"ℹ️ Column already exists: {e}")

conn.commit()
conn.close()
print("✅ Migration 004 complete!")
