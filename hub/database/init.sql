\connect sensors

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature FLOAT,
    humidity FLOAT,
    soil_moisture FLOAT,
    location VARCHAR(100),
    battery_voltage FLOAT
);

-- TimescaleDB hypertable
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);

-- Index for fast queries
CREATE INDEX idx_sensor_data_device_timestamp ON sensor_data(device_id, timestamp DESC);