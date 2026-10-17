
-- 1. Drive storage summary
SELECT
    mount_point,
    total_bytes,
    used_bytes,
    free_bytes,
    ROUND(
        100.0 * used_bytes / NULLIF(total_bytes, 0), 2
    ) AS utilization_percent
FROM drives
ORDER BY utilization_percent DESC;

-- 2. Scan history
SELECT
    d.mount_point,
    s.scan_id,
    s.started_at,
    s.status,
    h.captured_at,
    h.used_bytes,
    h.free_bytes
FROM drive_usage_history h
JOIN drives d ON d.drive_id = h.drive_id
JOIN scan_sessions s ON s.scan_id = h.scan_id
ORDER BY h.captured_at DESC;


-- 3. Total number of registered drives
SELECT COUNT(*) AS total_drives
FROM drives;
-- 3. Drive usage history
SELECT
    d.mount_point,
    h.total_bytes,
    h.used_bytes,
    h.free_bytes,
    h.captured_at
FROM drive_usage_history h
JOIN drives d ON d.drive_id = h.drive_id
ORDER BY h.captured_at DESC;