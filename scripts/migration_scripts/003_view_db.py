import sqlite3
import os

# Paths
# Calculate project root
current_dir = os.path.abspath(os.path.dirname(__file__))
while os.path.basename(current_dir) != 'smart_allotment':
    parent = os.path.dirname(current_dir)
    if parent == current_dir:
        raise RuntimeError("Could not find smart_allotment project root")
    current_dir = parent

PROJECT_ROOT = current_dir
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

# 3. LAST NOTIFIED EVENTS PER SENSOR (most recent notification per sensor)
print("\n3. LAST NOTIFIED EVENTS PER SENSOR:")
cursor.execute("""
    SELECT DISTINCT sensor_name, 
           MAX(last_notified) as last_notified,
           alert_type, value, timestamp
    FROM alerts 
    WHERE last_notified IS NOT NULL
    GROUP BY sensor_name
    ORDER BY last_notified DESC
""")
print("  Sensor    | Last Notified | Alert Type  | Value")
print("  ----------|---------------|-------------|------")
for row in cursor.fetchall():
    sensor, notified, alert_type, value, ts = row
    # Format datetime to fit column (cut microseconds)
    notified_short = str(notified).split('.')[0] if notified else "None"
    print(f"  {sensor:<9} | {notified_short:<14} | {alert_type[:10]:<10} | {value:>5.1f}")

# 4. Show recent sensor readings (last 5 per sensor)
print("\n4. RECENT SENSOR READINGS (last 5 each):")
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

# 5. Last Notified per sensor (unique alerts)
print("\n5. LAST NOTIFIED BY ALERT TYPE:")
cursor.execute("""
    SELECT alert_type, sensor_name,
           MAX(last_notified) as last_notified,
           MAX(value) as latest_value
    FROM alerts 
    WHERE last_notified IS NOT NULL
    GROUP BY alert_type, sensor_name
    ORDER BY last_notified DESC
    LIMIT 10
""")
print(" Alert Type          | Sensor | Time                | Value")
print(" --------------------|--------|---------------------|------")
for row in cursor.fetchall():
    alert_type, sensor, notified, value = row
    notified_short = str(notified).split('.')[0] if notified else "None"
    print(f" {alert_type[:20]:<20} | {sensor:<6} | {notified_short:<17} | {value:>5.1f}")

# 6. Show record counts
print("\n6. RECORD COUNTS:")
cursor.execute("SELECT 'alerts' as table_name, COUNT(*) as count FROM alerts UNION ALL SELECT 'sensor_readings', COUNT(*) FROM sensor_readings")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} records")

# 7. Database file size (SQL + filesystem)
print("\n7. DATABASE SIZE:")
stat_size = os.path.getsize(DB_PATH)
cursor.execute("SELECT page_count * page_size AS db_size FROM pragma_page_count(), pragma_page_size()")
sql_size = cursor.fetchone()[0]

size_mb = stat_size / (1024 * 1024)
print(f" File size:   {size_mb:.1f} MB ({stat_size:,} bytes)")
print(f" SQL size:   {sql_size / (1024*1024):.1f} MB ({sql_size:,} bytes)")

conn.close()
print("\nDone!")
