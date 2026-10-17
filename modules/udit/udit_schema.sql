
CREATE TABLE IF NOT EXISTS scan_sessions (
    scan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'completed', 'failed'))
);

CREATE TABLE IF NOT EXISTS drives (
    drive_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mount_point TEXT NOT NULL UNIQUE,
    filesystem VARCHAR(50),
    total_bytes BIGINT NOT NULL DEFAULT 0 CHECK (total_bytes >= 0),
    used_bytes BIGINT NOT NULL DEFAULT 0 CHECK (used_bytes >= 0),
    free_bytes BIGINT NOT NULL DEFAULT 0 CHECK (free_bytes >= 0),
    last_scanned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drive_usage_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    drive_id BIGINT NOT NULL REFERENCES drives(drive_id),
    scan_id BIGINT NOT NULL REFERENCES scan_sessions(scan_id),
    total_bytes BIGINT NOT NULL CHECK (total_bytes >= 0),
    used_bytes BIGINT NOT NULL CHECK (used_bytes >= 0),
    free_bytes BIGINT NOT NULL CHECK (free_bytes >= 0),
    captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_drive_usage_history_drive_id
    ON drive_usage_history(drive_id);

CREATE INDEX IF NOT EXISTS idx_drive_usage_history_scan_id
    ON drive_usage_history(scan_id);

CREATE INDEX IF NOT EXISTS idx_scan_sessions_started_at
    ON scan_sessions(started_at);
