CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS flight_snapshot ((
    id SERIAL PRIMARY KEY,
    icao24 TEXT,
    callsign TEXT,
    origin_country TEXT,
    time_position TIMESTAMP,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    geo_altitude DOUBLE PRECISION,
    on_ground BOOLEAN,
    region TEXT NOT NULL
) stored 
);
