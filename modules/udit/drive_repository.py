
import os
import psycopg2


def get_connection():
    """Connect to the PostgreSQL test database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "smart_file_manager_test"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
    )


def save_drive_scan(drives):
    """Save drive details and usage history transactionally."""
    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO scan_sessions (status)
                    VALUES ('running')
                    RETURNING scan_id;
                """)
                scan_id = cur.fetchone()[0]

                for drive in drives:
                    cur.execute("""
                        INSERT INTO drives (
                            mount_point, filesystem,
                            total_bytes, used_bytes, free_bytes,
                            last_scanned_at
                        )
                        VALUES (%s, %s, %s, %s, %s,
                                CURRENT_TIMESTAMP)
                        ON CONFLICT (mount_point)
                        DO UPDATE SET
                            filesystem = EXCLUDED.filesystem,
                            total_bytes = EXCLUDED.total_bytes,
                            used_bytes = EXCLUDED.used_bytes,
                            free_bytes = EXCLUDED.free_bytes,
                            last_scanned_at = CURRENT_TIMESTAMP
                        RETURNING drive_id;
                    """, (
                        drive["mount_point"],
                        drive["filesystem"],
                        drive["total_bytes"],
                        drive["used_bytes"],
                        drive["free_bytes"],
                    ))

                    drive_id = cur.fetchone()[0]

                    cur.execute("""
                        INSERT INTO drive_usage_history (
                            drive_id, scan_id,
                            total_bytes, used_bytes, free_bytes
                        )
                        VALUES (%s, %s, %s, %s, %s);
                    """, (
                        drive_id,
                        scan_id,
                        drive["total_bytes"],
                        drive["used_bytes"],
                        drive["free_bytes"],
                    ))

                cur.execute("""
                    UPDATE scan_sessions
                    SET status = 'completed',
                        completed_at = CURRENT_TIMESTAMP
                    WHERE scan_id = %s;
                """, (scan_id,))

        return scan_id

    finally:
        conn.close()
