"""PostgreSQL repository for Movement_History."""
from typing import Optional


def create_movement(conn, file_id: int, source_path: str,
                    destination_path: str) -> int:
    """Insert PENDING history and return its history_id. conn is a psycopg connection."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO Movement_History
                (file_id, source_path, destination_path, status)
            VALUES (%s, %s, %s, 'PENDING')
            RETURNING history_id
            """,
            (file_id, source_path, destination_path),
        )
        history_id = cur.fetchone()[0]
    conn.commit()
    return history_id


def update_movement(conn, history_id: int, status: str,
                    error_message: Optional[str] = None) -> None:
    if status not in {"PENDING", "DONE", "FAILED"}:
        raise ValueError("Invalid movement status")
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE Movement_History
               SET status = %s, error_message = %s,
                   moved_at = CASE WHEN %s = 'DONE'
                                   THEN CURRENT_TIMESTAMP ELSE moved_at END
             WHERE history_id = %s
            """,
            (status, error_message, status, history_id),
        )
    conn.commit()


def get_pending_movements(conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT history_id, file_id, source_path, destination_path
                 FROM Movement_History
                WHERE status = 'PENDING'
                ORDER BY history_id"""
        )
        return cur.fetchall()
