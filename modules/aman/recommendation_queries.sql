-- modules/aman/recommendation_queries.sql
-- ==========================================
-- Reference SQL queries for the Recommendations table.
-- Use parameterised queries ($1, $2, …) when embedding in Python (psycopg2 / asyncpg).
-- Replace placeholder UUIDs with real values from your application.

-- ============================================================
-- 1. Insert a new recommendation
-- ============================================================
INSERT INTO Recommendations (
    recommendation_id,
    file_path,
    recommendation_type,
    suggested_action,
    destination,
    reason,
    priority,
    status,
    created_at,
    updated_at
) VALUES (
    $1,   -- recommendation_id  (UUID)
    $2,   -- file_path          (TEXT)
    $3,   -- recommendation_type (VARCHAR 50)
    $4,   -- suggested_action   (VARCHAR 100)
    $5,   -- destination        (TEXT or NULL)
    $6,   -- reason             (TEXT)
    $7,   -- priority           ('LOW' | 'MEDIUM' | 'HIGH')
    'PENDING',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. Update a recommendation's status
-- ============================================================
UPDATE Recommendations
SET    status     = $1,          -- 'APPROVED' | 'REJECTED' | 'COMPLETED'
       updated_at = CURRENT_TIMESTAMP
WHERE  recommendation_id = $2    -- UUID
  AND  status = 'PENDING';       -- guard: only advance from PENDING


-- ============================================================
-- 3. List all PENDING recommendations, highest priority first
-- ============================================================
SELECT recommendation_id,
       file_path,
       recommendation_type,
       suggested_action,
       destination,
       priority,
       reason,
       created_at
FROM   Recommendations
WHERE  status = 'PENDING'
ORDER BY
    CASE priority
        WHEN 'HIGH'   THEN 1
        WHEN 'MEDIUM' THEN 2
        ELSE               3
    END,
    created_at DESC;


-- ============================================================
-- 4. Count recommendations by type and status
-- ============================================================
SELECT recommendation_type,
       status,
       COUNT(*) AS total
FROM   Recommendations
GROUP  BY recommendation_type, status
ORDER  BY recommendation_type, status;


-- ============================================================
-- 5. Find files with duplicate hashes
--    (Requires the shared Files table to have a file_hash column.
--     Verify the schema before running this query.)
-- ============================================================
-- SELECT f.file_path,
--        f.file_hash,
--        COUNT(*) AS occurrences
-- FROM   Files f
-- WHERE  f.file_hash IS NOT NULL
-- GROUP  BY f.file_path, f.file_hash
-- HAVING COUNT(*) > 1
-- ORDER  BY occurrences DESC;
--
-- NOTE: Uncomment and adjust column names once the shared Files table
--       schema has been confirmed by your team.


-- ============================================================
-- 6. Latest recommendation per file  (window function)
-- ============================================================
WITH RankedRecommendations AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY file_path
               ORDER BY created_at DESC
           ) AS rn
    FROM   Recommendations
)
SELECT recommendation_id,
       file_path,
       recommendation_type,
       suggested_action,
       status,
       priority,
       created_at
FROM   RankedRecommendations
WHERE  rn = 1
ORDER  BY file_path;


-- ============================================================
-- 7. Summarise pending recommendations using a CTE
-- ============================================================
WITH PendingSummary AS (
    SELECT suggested_action,
           priority,
           COUNT(*) AS total_pending
    FROM   Recommendations
    WHERE  status = 'PENDING'
    GROUP  BY suggested_action, priority
)
SELECT suggested_action,
       priority,
       total_pending
FROM   PendingSummary
ORDER  BY
    CASE priority
        WHEN 'HIGH'   THEN 1
        WHEN 'MEDIUM' THEN 2
        ELSE               3
    END,
    total_pending DESC;


-- ============================================================
-- 8. Join Recommendations with the shared Files table
--    (Verify Files table schema before enabling this query.)
-- ============================================================
-- SELECT r.recommendation_id,
--        r.file_path,
--        r.recommendation_type,
--        r.suggested_action,
--        r.status,
--        f.file_size,
--        f.file_hash,
--        f.owner
-- FROM   Recommendations r
-- JOIN   Files f ON f.file_path = r.file_path
-- WHERE  r.status = 'PENDING'
-- ORDER  BY r.created_at DESC;
--
-- NOTE: Uncomment and adjust once the shared Files table
--       schema has been confirmed by your team.
