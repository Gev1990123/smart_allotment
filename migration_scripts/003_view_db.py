import sqlite3
import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'smart_allotment.db')

print("Smart Allotment Database Viewer")
print("=" * 50)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Show all tables
print("\n1. TABLES:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"{table[0]}")

# 2. Show recent alerts (last 10)
print("\n2. RECENT ALERTS (last 10):")
cursor.execute("""
    SELECT alert_type, sensor_name, value, timestamp, last_notified 
    FROM alerts 
    ORDER BY timestamp DESC 
    LIMIT 10
""")
print("  Type          | Sensor | Value | Time                | Last Notified")
print("  ---------------|--------|-------|---------------------|--------------")
for row in cursor.fetchall():
    alert_type, sensor, value, ts, notified = row
    notified = notified or "None"
    print(f"  {alert_type[:13]:<13} | {sensor}   | {value:>5} | {ts} | {notified}")

# 3. Show recent sensor readings (last 5 per sensor)
print("\n3. RECENT SENSOR READINGS (last 5 each):")
for sensor_type in ['soil_moisture', 'temperature', 'light']:
    print(f"\n  {sensor_type.upper()}:")
    cursor.execute("""
        SELECT sensor_type, value, timestamp 
        FROM sensor_readings 
        WHERE sensor_type=? 
        ORDER BY timestamp DESC 
        LIMIT 5
    """, (sensor_type,))
    print("    Value | Time")
    print("    ------|----------")
    for row in cursor.fetchall():
        print(f"    {row[1]:>5} | {row[2]}")

# 4. Show record counts
print("\n4. RECORD COUNTS:")
cursor.execute("SELECT 'alerts' as table_name, COUNT(*) as count FROM alerts UNION ALL SELECT 'sensor_readings', COUNT(*) FROM sensor_readings")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} records")

conn.close()
print("\nDone!")
