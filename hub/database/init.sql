-- Docker-compatible Smart Allotment database init
-- Works automatically via docker-entrypoint-initdb.d

-- Ensure we're in the right database context
DO $$
BEGIN
    -- Create database if not exists
    CREATE DATABASE sensors;
EXCEPTION
    WHEN duplicate_database THEN
        RAISE NOTICE 'Database sensors already exists, skipping creation';
END
$$;

-- Connect to sensors database
\c sensors mqtt

-- Create user with correct permissions
CREATE USER mqtt WITH SUPERUSER CREATEDB PASSWORD 'smartallotment2026';
GRANT ALL PRIVILEGES ON DATABASE sensors TO mqtt;

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create sensor_data hypertable
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    moisture INTEGER,
    temperature FLOAT,
    humidity FLOAT,
    battery_voltage FLOAT,
    rssi INTEGER
);

-- Convert to hypertable
SELECT create_hypertable('sensor_data', 'time');

-- Indexes for fast queries
CREATE INDEX ON sensor_data (sensor_id, time DESC);
CREATE INDEX ON sensor_data (time DESC) WHERE moisture IS NOT NULL;

-- MQTT topic subscription trigger
CREATE OR REPLACE FUNCTION mqtt_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO sensor_data (time, sensor_id, moisture, temperature, humidity, battery_voltage, rssi)
    VALUES (
        NOW(),
        NEW.sensor_id,
        NEW.moisture,
        NEW.temperature,
        NEW.humidity,
        NEW.battery_voltage,
        NEW.rssi
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;