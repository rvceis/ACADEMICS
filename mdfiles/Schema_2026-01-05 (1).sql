-- Schema: Schema_2026-01-05
-- Version: 4
-- Created by: admin
-- Exported: 2026-02-02T21:15:16.157619

CREATE TABLE IF NOT EXISTS schema_2026_01_05 (
    id SERIAL PRIMARY KEY,
    model VARCHAR(255),
    task VARCHAR(255),
    rmse FLOAT,
    mae FLOAT
);