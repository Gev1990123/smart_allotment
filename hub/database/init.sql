cat > database/init.sql << 'EOF'
-- Smart Allotment PostgreSQL (no TimescaleDB)
CREATE DATABASE sensors;
CREATE USER mqtt WITH SUPERUSER PASSWORD 'smartallotment2026';
GRANT ALL ON DATABASE sensors TO mqtt;
\c sensors mqtt

CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    moisture INTEGER, 
    temperature FLOAT, 
    humidity FLOAT,
    battery_voltage FLOAT, 
    rssi INTEGER,
    PRIMARY KEY (time, sensor_id)
);

CREATE INDEX idx_sensor_time ON sensor_data (sensor_id, time DESC);
EOF
