#!/bin/bash
# Database initialization script for PostgreSQL with PostGIS

# Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create tables
CREATE TABLE IF NOT EXISTS air_quality_data (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(50) NOT NULL,
    pm25 FLOAT,
    pm10 FLOAT,
    no2 FLOAT,
    o3 FLOAT,
    co FLOAT,
    so2 FLOAT,
    aqi INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    forecast_timestamp TIMESTAMP NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    pm25_forecast FLOAT,
    pm10_forecast FLOAT,
    no2_forecast FLOAT,
    o3_forecast FLOAT,
    aqi_forecast INTEGER,
    confidence_score FLOAT
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- Create indexes
CREATE INDEX idx_air_quality_location ON air_quality_data USING GIST(location);
CREATE INDEX idx_air_quality_timestamp ON air_quality_data(timestamp);
CREATE INDEX idx_forecasts_location ON forecasts USING GIST(location);
CREATE INDEX idx_forecasts_timestamp ON forecasts(forecast_timestamp);
CREATE INDEX idx_alerts_location ON alerts USING GIST(location);
CREATE INDEX idx_alerts_status ON alerts(status);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
