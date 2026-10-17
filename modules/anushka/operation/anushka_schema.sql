
-- Audit log for file path changes (test database only)
CREATE TABLE IF NOT EXISTS file_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT NOT NULL,
    old_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION log_test_file_path_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.file_path IS DISTINCT FROM NEW.file_path THEN
        INSERT INTO file_audit_log (
            file_id,
            old_path,
            new_path
        )
        VALUES (
            NEW.file_id,
            OLD.file_path,
            NEW.file_path
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_test_file_path_audit
ON test_files;

CREATE TRIGGER trg_test_file_path_audit
AFTER UPDATE OF file_path ON test_files
FOR EACH ROW
EXECUTE FUNCTION log_test_file_path_change();
