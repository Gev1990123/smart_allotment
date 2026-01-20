
----------------------------------------------------------------------
-- Smart Allotment PostgreSQL Schema
-- This file initializes the hub database
----------------------------------------------------------------------

-- Drop tables if they already exist (optional for rebuilds)
DROP TABLE IF EXISTS pump_events;
DROP TABLE IF EXISTS telemetry;
DROP TABLE IF EXISTS sites;

----------------------------------------------------------------------
-- Sites table
-- Each Raspberry Pi node represents one site/location
----------------------------------------------------------------------

CREATE TABLE sites (
    id SERIAL PRIMARY KEY,
    site_code VARCHAR(50) UNIQUE NOT NULL,
    friendly_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------------------------------------------
-- Telemetry table
-- Stores sensor measurements from each site
----------------------------------------------------------------------

CREATE TABLE telemetry (
    id BIGSERIAL PRIMARY KEY,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,

    -- Standard sensor values
    soil_moisture NUMERIC,
    water_level NUMERIC,
    humidity NUMERIC,
    temperature NUMERIC,

    -- Optional JSON field for flexible future sensor data
    raw_json JSONB,

    -- Index for fast queries
    INDEX (site_id, timestamp)
);

----------------------------------------------------------------------
-- Pump events table
-- Records water pump activity (manual or automated)
----------------------------------------------------------------------

CREATE TABLE pump_events (
    id SERIAL PRIMARY KEY,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    event_time TIMESTAMP NOT NULL,
    action VARCHAR(10) NOT NULL,     -- 'on' or 'off'
    triggered_by VARCHAR(50)         -- 'manual', 'rule', 'mqtt', etc.
);

----------------------------------------------------------------------
-- End of schema
----------------------------------------------------------------------
