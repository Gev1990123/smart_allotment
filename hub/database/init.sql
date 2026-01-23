cat > database/init.sql << 'EOF'
CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTAMPTZ NOT NULL,
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