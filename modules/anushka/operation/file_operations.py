
import os

from modules.anushka.operation.safe_move import safe_move
from modules.anushka.operation.history_repository import (
    create_movement,
    update_movement,
)


def move_file(
    conn,
    file_id: int,
    destination: str,
    table_name: str = "Files",
) -> bool:
    """Move a file and record its movement history.

    table_name must be either Files or test_files.
    Both tables must contain file_id and file_path columns.
    """
    if table_name not in {"Files", "test_files"}:
        raise ValueError("Unsupported table name")

    history_id = None
    source = None

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT file_path FROM {table_name} WHERE file_id = %s",
                (file_id,),
            )
            row = cur.fetchone()

        if row is None:
            return False

        source = row[0]
        history_id = create_movement(
            conn, file_id, source, destination
        )

        if not safe_move(source, destination):
            update_movement(
                conn, history_id, "FAILED", "Filesystem move failed"
            )
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {table_name} SET file_path = %s "
                    "WHERE file_id = %s",
                    (destination, file_id),
                )

            update_movement(conn, history_id, "DONE")
            conn.commit()
            return True

        except Exception:
            conn.rollback()

            # Best-effort attempt to restore the original file location.
            try:
                if source and not os.path.exists(source):
                    safe_move(destination, source)
            except Exception:
                pass

            update_movement(
                conn, history_id, "FAILED", "Database update failed"
            )
            return False

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

        if history_id is not None:
            try:
                update_movement(
                    conn, history_id, "FAILED",
                    "Unexpected operation error",
                )
            except Exception:
                pass

        return False
