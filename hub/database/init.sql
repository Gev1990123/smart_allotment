CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT,
    sensor_id VARCHAR(50) NOT NULL,
    moisture INTEGER,
    temperature FLOAT,
    light INTEGER,
    humidity FLOAT,
    battery_voltage FLOAT,
    rssi INTEGER,
    PRIMARY KEY (time, sensor_id)
);

CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_data (sensor_id, time DESC);