> database/init.sql  # Empty the file
cat >> database/init.sql << 'EOF'
-- Smart Allotment PostgreSQL - Docker auto-creates DB/user
CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    moisture INTEGER,
    temperature FLOAT,
    humidity FLOAT,
    battery_voltage FLOAT,
    rssi INTEGER,
    PRIMARY KEY (time, sensor_id)
);

CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_data (sensor_id, time DESC);
EOF
