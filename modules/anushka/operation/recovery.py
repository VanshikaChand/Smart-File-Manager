
"""Conservative recovery for pending file movements."""

import os

from modules.anushka.operation.history_repository import (
    get_pending_movements,
    update_movement,
)


def recover_pending_movements(conn, table_name="Files"):
    """Reconcile pending movements without making destructive assumptions.

    Supported tables:
        Files: production schema (use only with explicit approval).
        test_files: isolated integration-test schema.
    """
    if table_name not in {"Files", "test_files"}:
        raise ValueError("Unsupported table name")

    summary = {
        "done": 0,
        "failed": 0,
        "needs_review": 0,
    }

    pending_movements = get_pending_movements(conn)

    for history_id, file_id, source, destination in pending_movements:
        source_exists = os.path.isfile(source)
        destination_exists = os.path.isfile(destination)

        # Destination exists and source is gone: likely completed before a crash.
        if destination_exists and not source_exists:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE {table_name} "
                        "SET file_path = %s WHERE file_id = %s",
                        (destination, file_id),
                    )

                conn.commit()
                update_movement(conn, history_id, "DONE")
                summary["done"] += 1

            except Exception:
                conn.rollback()
                summary["needs_review"] += 1

        # Source exists and destination is missing: movement did not complete.
        elif source_exists and not destination_exists:
            try:
                update_movement(
                    conn,
                    history_id,
                    "FAILED",
                    "Move did not complete",
                )
                summary["failed"] += 1
            except Exception:
                conn.rollback()
                summary["needs_review"] += 1

        # Both exist or neither exists: leave pending for manual review.
        else:
            summary["needs_review"] += 1

    return summary
