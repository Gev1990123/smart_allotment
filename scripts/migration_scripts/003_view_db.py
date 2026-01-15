#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# PostgreSQL connection from .env
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

print("Smart Allotment PostgreSQL Viewer")
print("=" * 50)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cursor = conn.cursor()

# 1. Show all tables
print("\n1. TABLES:")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
tables = cursor.fetchall()
for table in tables:
    print(f"  {table[0]}")

# 2. Recent alerts (last 10)
print("\n2. RECENT ALERTS (last 10):")
cursor.execute("""
    SELECT alert_type, sensor_name, value, timestamp, last_notified, status 
    FROM alerts 
    ORDER BY timestamp DESC 
    LIMIT 10
""")
alerts = cursor.fetchall()
print("  Type           | Sensor | Value | Time                | Last Notified | Status    |")
print("  ---------------|--------|-------|---------------------|--------------|-----------|")
for row in alerts:
    alert_type, sensor, value, ts, notified, status = row
    notified = notified or "None"
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "None"
    notified_str = notified.strftime("%Y-%m-%d %H:%M") if notified else "None"
    print(f"  {str(alert_type)[:13]:<13} | {sensor:<6} | {value:>5.1f} | {ts_str} | {notified_str:<12} | {status}")

# 3. LAST NOTIFIED EVENTS PER SENSOR
print("\n3. LAST NOTIFIED EVENTS PER SENSOR:")
cursor.execute("""
    SELECT sensor_name, 
           MAX(last_notified) as last_notified,
           alert_type, value, timestamp, status
    FROM alerts 
    WHERE last_notified IS NOT NULL
    GROUP BY sensor_name, alert_type, value, timestamp, status
    ORDER BY last_notified DESC
    LIMIT 10
""")
notified_events = cursor.fetchall()
print(" Sensor   | Last Notified      | Alert Type        | Value | Status    |")
print(" --------|---------------------|-------------------|-------|-----------|")
for row in notified_events:
    sensor, notified, alert_type, value, ts, status = row
    notified_short = notified.strftime("%Y-%m-%d %H:%M") if notified else "None"
    print(f" {sensor:<8} | {notified_short:<17} | {str(alert_type)[:17]:<17} | {value:>5.1f} | {status}")

# 4. Recent sensor readings (last 5 per sensor)
print("\n4. RECENT SENSOR READINGS (last 5 each):")
for sensor_type in ['soil_moisture', 'temperature', 'light']:
    print(f"\n  {sensor_type.upper()}:")
    cursor.execute("""
        SELECT sensor_type, value, timestamp 
        FROM sensor_readings 
        WHERE sensor_type = %s 
        ORDER BY timestamp DESC 
        LIMIT 5
    """, (sensor_type,))
    readings = cursor.fetchall()
    print("    Value | Time")
    print("    ------|----------")
    for row in readings:
        value, ts = row[1], row[2]
        ts_str = ts.strftime("%H:%M:%S")
        print(f"    {value:>6.1f} | {ts_str}")

# 5. RECORD COUNTS
print("\n5. RECORD COUNTS:")
cursor.execute("""
    SELECT 'alerts' as table_name, COUNT(*) as count 
    FROM alerts 
    UNION ALL 
    SELECT 'sensor_readings', COUNT(*) 
    FROM sensor_readings
""")
counts = cursor.fetchall()
for row in counts:
    print(f"  {row[0]}: {row[1]:,} records")

# 6. Database size (PostgreSQL stats)
print("\n6. DATABASE SIZE:")
cursor.execute("""
    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
""")
db_size = cursor.fetchone()[0]
print(f"  Database size: {db_size}")

# Close connection
cursor.close()
conn.close()
print("\n✅ PostgreSQL Database Viewer Complete!")
