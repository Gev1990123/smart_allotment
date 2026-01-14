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

# 5. Database file size (SQL + filesystem)
print("\n5. DATABASE SIZE:")
stat_size = os.path.getsize(DB_PATH)
cursor.execute("SELECT page_count * page_size AS db_size FROM pragma_page_count(), pragma_page_size()")
sql_size = cursor.fetchone()[0]

size_mb = stat_size / (1024 * 1024)
print(f" File size:   {size_mb:.1f} MB ({stat_size:,} bytes)")
print(f" SQL size:   {sql_size / (1024*1024):.1f} MB ({sql_size:,} bytes)")

conn.close()
print("\nDone!")
